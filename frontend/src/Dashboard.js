import * as React from 'react';
import { styled, createTheme, ThemeProvider, alpha } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import MuiDrawer from '@mui/material/Drawer';
import Box from '@mui/material/Box';
import MuiAppBar, { AppBarProps as MuiAppBarProps } from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import Badge from '@mui/material/Badge';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Link from '@mui/material/Link';
import Slider from '@mui/material/Slider';
import Stack from '@mui/material/Stack';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import NotificationsIcon from '@mui/icons-material/Notifications';
import ListItemButton from '@mui/material/ListItemButton';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import LinkIcon from '@mui/icons-material/Link';
import LinkOffIcon from '@mui/icons-material/LinkOff';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import SearchIcon from '@mui/icons-material/Search';
import CytoscapeComponent from "react-cytoscapejs";
import ConstructionIcon from '@mui/icons-material/Construction';
import cytoscape from 'cytoscape';
import fcose from 'cytoscape-fcose';
import dagre from 'cytoscape-dagre';
import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';


// ?????????????????????
const drawerWidth = 300;

// ??????????????????????????????
const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})(({ theme, open }) => ({
  zIndex: theme.zIndex.drawer + 1,
  transition: theme.transitions.create(['width', 'margin'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const Drawer = styled(MuiDrawer, { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme, open }) => ({
    '& .MuiDrawer-paper': {
      position: 'relative',
      whiteSpace: 'nowrap',
      width: drawerWidth,
      transition: theme.transitions.create('width', {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.enteringScreen,
      }),
      boxSizing: 'border-box',
      ...(!open && {
        overflowX: 'hidden',
        transition: theme.transitions.create('width', {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.leavingScreen,
        }),
        width: theme.spacing(7),
        [theme.breakpoints.up('sm')]: {
          // ??????????????????????????????????????????
          width: theme.spacing(7),
        },
      }),
    },
  }),
);

const Search = styled('div')(({ theme }) => ({
  position: 'relative',
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  '&:hover': {
    backgroundColor: alpha(theme.palette.common.white, 0.25),
  },
  marginRight: theme.spacing(2),
  marginLeft: 0,
  width: '100%',
  [theme.breakpoints.up('sm')]: {
    marginLeft: theme.spacing(3),
    width: 'auto',
  },
}));

const SearchIconWrapper = styled('div')(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: '100%',
  position: 'absolute',
  pointerEvents: 'none',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}));

const StyledAutocomplete = styled(Autocomplete)((props) => ({
  color: 'inherit',
  "& .MuiAutocomplete-inputRoot": {
    color: "white",
    '&[class*="MuiOutlinedInput-root"] .MuiAutocomplete-input:first-child': {
      // Default left padding is 6px
      paddingLeft: 50
    },
    "& .MuiOutlinedInput-notchedOutline": {
      borderColor: "#3e87d9"
    },
    "&:hover .MuiOutlinedInput-notchedOutline": {
      borderColor: "#3e87d9"
    },
    "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
      borderColor: "#5398dd"
    },
    "&.Mui-focused .fieldset": {
      borderColor: "#3e87d9"
    }
  }
}));

// cytoscape?????????
cytoscape.use(fcose);
cytoscape.use(dagre);

// ?????????????????????????????????????????????
const DashboardContent = (props) => {
  // ??????
  const _default_target_level = 1;
  const _default_source_level = 1;
  const _default_layout_name = 'fcose';
  const mdTheme = createTheme();
  const defaultMarks = [
    { value: 0, label: "0" },
  ];

  // ??????????????????
  var _cy = null;

  // ???????????????????????????
  const [open, setOpen] = React.useState(true);
  const toggleDrawer = () => {
    setOpen(!open);
  };


  // inner function
  function getTableNodes(table_name, target_level, source_level) {
    if (!table_name) {
      return
    }

    const query_params = new URLSearchParams({
      table_name: table_name,
      target_level: target_level,
      source_level: source_level
    });

    const requestOptions = {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    };

    fetch(`${process.env.REACT_APP_BASE_URL}/api/v1/tablenodes?${query_params}`, requestOptions)
      .then((response) => response.json())
      .then((json) => {
        //console.log(JSON.stringify(json, null, 2));
        _cy.json({ elements: json.nodes });
        var layout = {
          name: layoutNameValue,
        };
        _cy.layout(layout).run();

        // target level?????????
        var targetLevelMarks = [];
        for (let ni = 0; ni <= json.params.max_target_level; ni++) {
          targetLevelMarks.push({ value: ni, label: ni.toString() })
        }
        setTargetLevelMarks(targetLevelMarks);
        if (targetLevelMarks.length === 0) {
          setTargetMaxLevelMarks(0);
          setTargetMinLevelMarks(0);
        } else {
          setTargetMaxLevelMarks(targetLevelMarks[targetLevelMarks.length - 1].value);
          setTargetMinLevelMarks(targetLevelMarks[0].value);
        }
        setTargetLevel(json.params.target_level);

        // source level?????????
        var sourceLevelMarks = [];
        for (let ni = 0; ni <= json.params.max_source_level; ni++) {
          sourceLevelMarks.push({ value: ni, label: ni.toString() })
        }
        setSourceLevelMarks(sourceLevelMarks);
        if (sourceLevelMarks.length === 0) {
          setSourceMaxLevelMarks(0);
          setSourceMinLevelMarks(0);
        } else {
          setSourceMaxLevelMarks(sourceLevelMarks[sourceLevelMarks.length - 1].value);
          setSourceMinLevelMarks(sourceLevelMarks[0].value);
        }
        setSourceLevel(json.params.source_level);

      });
  }

  // ????????????????????????
  const [layoutNameValue, setLayoutNameValue] = React.useState('');
  const handleGraphLayoutChange = (event) => { //event: SelectChangeEvent
    setLayoutNameValue(event.target.value);
    var layout = {
      name: event.target.value,
      padding: 50
    };
    if (event.target.value === 'dagre') {
      layout = {
        name: 'dagre',
        rankDir: 'BT',
        padding: 50
      }
    }
    _cy.layout(layout).run();
  };

  // ???????????????????????????????????????????????????
  const [autoCompleteList, setAutoCompleteList] = React.useState(['']);
  const [searchText, setSearchText] = React.useState('');
  const handleSearchChange = (event, value) => {
    var table_name = value;
    setSearchText(table_name);
    getTableNodes(table_name, _default_target_level, _default_source_level);
  };

  // ????????????????????????
  const [targetLevelMarks, setTargetLevelMarks] = React.useState([]);
  const [targetMaxLevelMarks, setTargetMaxLevelMarks] = React.useState(0);
  const [targetMinLevelMarks, setTargetMinLevelMarks] = React.useState(0);
  const [targetLevel, setTargetLevel] = React.useState(0);

  const handleTargetLevelChange = (event) => {
    var target_level = event.target.value;
    //console.log(`table=${searchText} target=${target_level} source=${sourceLevel}`);
    getTableNodes(searchText, target_level, sourceLevel);
  };

  // ??????????????????
  const [sourceLevelMarks, setSourceLevelMarks] = React.useState([]);
  const [sourceMaxLevelMarks, setSourceMaxLevelMarks] = React.useState(0);
  const [sourceMinLevelMarks, setSourceMinLevelMarks] = React.useState(0);
  const [sourceLevel, setSourceLevel] = React.useState(0);

  const handleSourceLevelChange = (event) => {
    var source_level = event.target.value;
    //console.log(`table=${searchText} target=${targetLevel} source=${source_level}`);
    getTableNodes(searchText, targetLevel, source_level);
  };

  // Go To Document
  const edgeBaseUrl = 'https://github.com/tkeneix/datalineage-analyzer/blob/main/sample/';
  const nodeBaseUrl = 'https://github.com/tkeneix/datalineage-analyzer/blob/main/sampledoc/';
  const [gotoDocument, setGotoDocument] = React.useState('');

  // ????????????????????????
  React.useEffect(() => {
    setLayoutNameValue(_default_layout_name);

    fetch(`${process.env.REACT_APP_BASE_URL}/api/v1/tables`)
      .then((response) => response.json())
      .then((json) => setAutoCompleteList(json.tables));

    setTargetLevelMarks(defaultMarks);
    setSourceLevelMarks(defaultMarks);

    setTargetMaxLevelMarks(defaultMarks[defaultMarks.length - 1].value);
    setTargetMinLevelMarks(defaultMarks[0].value);

    setSourceMaxLevelMarks(defaultMarks[defaultMarks.length - 1].value);
    setSourceMinLevelMarks(defaultMarks[0].value);

    _cy.bind('click', 'edge', function (event) {
      var edgeData = event.target.data();
      //console.log(`click, edge=${JSON.stringify(edgeData, null, 2)}`);
      if (edgeData.hasOwnProperty('file_url')) {
        setGotoDocument(`${edgeBaseUrl}${edgeData.file_url}`);
      }
    });

    _cy.bind('click', 'node', function (event) {
      var nodeData = event.target.data();
      //console.log(`click, node=${JSON.stringify(nodeData, null, 2)}`);
      if (nodeData.hasOwnProperty('name')) {
        setGotoDocument(`${nodeBaseUrl}${nodeData.name}.html`);
      }
    });
  }, []);

  return (
    <ThemeProvider theme={mdTheme}>
      <Box sx={{ display: 'flex' }}>
        <CssBaseline />
        <AppBar position="absolute" open={open}>
          <Toolbar
            sx={{
              pr: '24px', // keep right padding when drawer closed
            }}
          >
            <IconButton
              edge="start"
              color="inherit"
              aria-label="open drawer"
              onClick={toggleDrawer}
              sx={{
                marginRight: '36px',
                ...(open && { display: 'none' }),
              }}
            >
              <MenuIcon />
            </IconButton>
            <Search>
              <SearchIconWrapper>
                <SearchIcon />
              </SearchIconWrapper>
              <Stack sx={{ width: 720, margin: "auto" }}>
                <StyledAutocomplete
                  id="test"
                  value={searchText}
                  options={autoCompleteList}
                  onChange={handleSearchChange}
                  sx={{ width: 720 }}
                  renderInput={(params) => <TextField
                    {...params}
                  />}
                />
              </Stack>
              {/* <LiveSearch /> */}
            </Search>
            <Box sx={{ flexGrow: 1 }} />
          </Toolbar>
        </AppBar>
        <Drawer variant="permanent" open={open}>
          <Toolbar
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              px: [1],
            }}
          >
            <Typography
              variant="h6"
              noWrap
              component="div"
              sx={{ display: { xs: 'none', sm: 'block' } }}
            >
              Data Lineage Visualizer
            </Typography>
            <IconButton onClick={toggleDrawer}>
              <ChevronLeftIcon />
            </IconButton>
          </Toolbar>
          <Divider />
          <List component="nav">
            {/* ????????????????????????????????? */}
            <ListItem>
              <ListItemIcon>
                <Badge badgeContent={targetLevel} color="info">
                  <ArrowUpwardIcon />
                </Badge>
              </ListItemIcon>
              <Slider
                aria-label="Always visible"
                defaultValue={1}
                value={targetLevel}
                onChange={handleTargetLevelChange}
                step={1}
                marks={targetLevelMarks}
                min={targetMinLevelMarks}
                max={targetMaxLevelMarks}
                valueLabelDisplay="off"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <Badge badgeContent={sourceLevel} color="info">
                  <ArrowDownwardIcon />
                </Badge>
              </ListItemIcon>
              <Slider
                aria-label="Always visible"
                defaultValue={1}
                onChange={handleSourceLevelChange}
                value={sourceLevel}
                step={1}
                marks={sourceLevelMarks}
                min={sourceMinLevelMarks}
                max={sourceMaxLevelMarks}
                valueLabelDisplay="off"
              />
            </ListItem>

            <ListItem>
              <ListItemIcon>
                <AccountTreeIcon />
              </ListItemIcon>
              <FormControl sx={{ m: 1, minWidth: 200 }} size="small">
                <InputLabel id="graphLayout">Graph Layout</InputLabel>
                <Select
                  labelId="graphLayout"
                  id="graphLayout"
                  value={layoutNameValue}
                  label="Graph Layout"
                  onChange={handleGraphLayoutChange}
                >
                  <MenuItem value="fcose" selected={true}>fcose</MenuItem>
                  <MenuItem value="dagre">dagre</MenuItem>
                  <MenuItem value="grid">grid</MenuItem>
                  <MenuItem value="random">random</MenuItem>
                  <MenuItem value="circle">circle</MenuItem>
                  <MenuItem value="concentric">concentric</MenuItem>
                  <MenuItem value="breadthfirst">breadthfirst</MenuItem>
                </Select>
              </FormControl>
            </ListItem>

            <ListItem>
              <ListItemIcon>
                <LinkIcon />
              </ListItemIcon>
              <ListItemButton component="a" target="_blank" href={gotoDocument}>
                <ListItemText primary="Go to Document" />
              </ListItemButton>
            </ListItem>

            <Divider sx={{ my: 1 }} />
            <ListItem>
              <ListItemIcon>
                <ConstructionIcon />
              </ListItemIcon>
              <ListItemText primary="Comming Soon" />
            </ListItem>
          </List>
        </Drawer>
        <Box
          component="main"
          sx={{
            backgroundColor: (theme) =>
              theme.palette.mode === 'light'
                ? theme.palette.grey[100]
                : theme.palette.grey[900],
            flexGrow: 1,
            height: '100vh',
            overflow: 'auto',
          }}
        >
          <Toolbar />
          <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            {/* <GraphCytospace/> */}
            <CytoscapeComponent
              cy={(cy) => { _cy = cy }}
              elements={CytoscapeComponent.normalizeElements([])}
              style={{
                position: "absolute",
                top: "100px",
                left: "50px",
                width: "100%",
                height: "100%",
              }}
              stylesheet={[
                {
                  selector: 'node',
                  style: {
                    opacity: 0.9,
                    label: "data(label)",
                    color: "#333333",
                    shape: 'round-rectangle',
                    width: 'label',
                    height: 'label',
                    padding: '6px'
                  }
                },
                {
                  selector: ":parent",
                  style: {
                    "background-opacity": 0.2,
                    'background-color': '#008000',
                    "line-color": "#cccccc"
                  }
                },
                {
                  "selector": 'edge',
                  "style": {
                    "target-arrow-color": "#cccccc",
                    "target-arrow-shape": "triangle",
                    "line-color": "#cccccc",
                    'arrow-scale': 1,
                    'curve-style': 'bezier'
                  }
                },
                {
                  selector: 'node[classes="source"]',
                  style: {
                    'background-color': '#191970',
                    'line-color': '#808080',
                    label: 'data(label)',
                    'color': 'white',
                    'text-halign': 'center',
                    'text-valign': 'center'
                  }
                },
                {
                  selector: 'node[classes="target"]',
                  style: {
                    'background-color': '#87ceeb',
                    'line-color': '#808080',
                    label: 'data(label)',
                    'color': 'black',
                    'text-halign': 'center',
                    'text-valign': 'center'
                  }
                },
                {
                  'selector': 'node[classes="root"]',
                  'style': {
                    'background-color': '#4169e1',
                    'line-color': '#808080',
                    label: 'data(label)',
                    'color': 'black',
                    'text-halign': 'center',
                    'text-valign': 'center'
                  }
                }
              ]}
              layout={{
                name: 'fcose',
                padding: 50
              }}
              minZoom={0.05}
            />
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default function Dashboard() {
  return <DashboardContent />;
}