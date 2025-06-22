import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Window controls
  minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
  maximizeWindow: () => ipcRenderer.invoke('maximize-window'),
  closeWindow: () => ipcRenderer.invoke('close-window'),
  
  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  
  // File operations
  openFile: () => ipcRenderer.invoke('open-file'),
  saveFile: (data: any) => ipcRenderer.invoke('save-file', data),
  
  // System notifications
  showNotification: (title: string, body: string) => 
    ipcRenderer.invoke('show-notification', { title, body }),
  
  // Storage operations
  setStorageItem: (key: string, value: string) => 
    ipcRenderer.invoke('set-storage-item', key, value),
  getStorageItem: (key: string) => 
    ipcRenderer.invoke('get-storage-item', key),
  removeStorageItem: (key: string) => 
    ipcRenderer.invoke('remove-storage-item', key),
    
  // Network status
  isOnline: () => ipcRenderer.invoke('is-online'),
  
  // Print functionality
  printToPDF: (options?: any) => ipcRenderer.invoke('print-to-pdf', options),
  print: () => ipcRenderer.invoke('print'),
});

// Type definitions for the exposed API
declare global {
  interface Window {
    electronAPI: {
      minimizeWindow: () => Promise<void>;
      maximizeWindow: () => Promise<void>;
      closeWindow: () => Promise<void>;
      getAppVersion: () => Promise<string>;
      openFile: () => Promise<string | null>;
      saveFile: (data: any) => Promise<boolean>;
      showNotification: (title: string, body: string) => Promise<void>;
      setStorageItem: (key: string, value: string) => Promise<void>;
      getStorageItem: (key: string) => Promise<string | null>;
      removeStorageItem: (key: string) => Promise<void>;
      isOnline: () => Promise<boolean>;
      printToPDF: (options?: any) => Promise<Buffer>;
      print: () => Promise<void>;
    };
  }
} 