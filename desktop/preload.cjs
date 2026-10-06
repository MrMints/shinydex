// Narrow IPC bridge; renderer code receives no Node.js or filesystem access.
const {contextBridge,ipcRenderer}=require('electron');
contextBridge.exposeInMainWorld('shinydexDesktop',{
  loadCollection:()=>ipcRenderer.invoke('collection:load'),
  saveCollection:record=>ipcRenderer.invoke('collection:save',record),
  backupCollection:()=>ipcRenderer.invoke('collection:backup'),
  importCollection:()=>ipcRenderer.invoke('collection:import'),
  updateStatus:()=>ipcRenderer.invoke('updates:status'),
  checkUpdates:()=>ipcRenderer.invoke('updates:check'),
  installVersion:tag=>ipcRenderer.invoke('updates:install',tag)
});
