# How to build this project

```
cd frontend
npm install
```

# How to create this project

```
npx create-react-app@3.3.1 frontend
cd frontend
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm install react-cytoscapejs
npm install cytoscape@3.8.1
npm install cytoscape-fcose
npm install cytoscape-dagre

sudo echo fs.inotify.max_user_watches=582222 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p

npm run build
```
