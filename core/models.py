from abc import ABCMeta, abstractmethod


class TableNode(metaclass=ABCMeta):
    def __init__(self, db_name, table_name, attributes=dict()) -> None:
        self.db = db_name
        self.name = table_name
        self.source_dict = dict()
        self.target_dict = dict()
        self.attr_dict = attributes

    def add_source(self, table_node) -> None:
        self.source_dict[table_node.name] = table_node
    
    def exist_source(self, table_name) -> bool:
        if self.source_dict.get(table_name) is not None:
            return True
        else:
            return False
    
    def add_target(self, table_node) -> None:
        self.target_dict[table_node.name] = table_node

    def exist_target(self, table_name) -> bool:
        if self.target_dict.get(table_name) is not None:
            return True
        else:
            return False
