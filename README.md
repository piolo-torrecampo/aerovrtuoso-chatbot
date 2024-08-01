# Aero VR Tuoso

**Note: Luanch the servers first.**

### STREAM SERVER
Requirements:
- OBS Studio
- Docker Container: illuspas/node-media-server

```docker run --name nms -d -p 1935:1935 -p 8000:8000 -p 8443:8443 illuspas/node-media-server```

**Configure OBS Studio**
1. Go to File -> Settings -> Stream
2. Fill the following parameters
  - Server: rtmp://localhost/live
  - Stream Key: STREAM_NAME
  
![alt text](./ReadMe%20Images/obs_configs.png)

### REDIS SERVER
```cd ./redis && docker-compose up```

### LUANCH WEB APP
1. ```npm install```
2. ```npm run dev```

