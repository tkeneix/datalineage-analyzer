from abc import ABCMeta, abstractmethod
import re
from environs import Env, EnvError


class ReplaceHandler(metaclass=ABCMeta):
    @abstractmethod
    def run(self, content, **kwargs):
        pass


class ReplaceSkipHandler(ReplaceHandler):
    def __init__(self, keyword) -> None:
        super().__init__()
        self.keyword = keyword
    
    def run(self, content, **kwargs) -> str:
        if re.match(self.keyword, content):
            # 正規表現に該当する場合は空文字を返し、上位でスキップする
            return ''
        else:
            return content


class ReplaceEnvHandler(ReplaceHandler):
    def __init__(self, env, default_after='ABC') -> None:
        super().__init__()
        self.env = env
        self.default_after = default_after
    
    def run(self, content, **kwargs) -> str:
        # findallの探索条件
        # ${で始まる
        # 間に半角スペースまたはピリオドを含まない
        # }で終わる
        env_element_list = re.findall('\${[^ |\.]+}', content)
        for env_element in env_element_list:
            env_key = env_element[2:-1]
            try:
                after = self.env(env_key)
            except EnvError as eer:
                after = self.default_after
            content = content.replace(env_element, after)
        return content


class ReplaceSkipPartHandler(ReplaceHandler):
    def __init__(self, start_keyword, end_keyword) -> None:
        super().__init__()
        self.start_keyword = start_keyword
        self.end_keyword = end_keyword
    
    def run(self, content, **kwargs) -> str:        
        ret_content = ''
        row_list = content.split('\n')
        is_commentout = False
        for row in row_list:
            if re.match(self.start_keyword, row.upper()):
                is_commentout = True
            
            if is_commentout and re.match(self.end_keyword, row.upper()):
                is_commentout = False
            
            if is_commentout:
                row = f"-- {row}"
            
            ret_content += f"{row}\n"
        
        return ret_content

