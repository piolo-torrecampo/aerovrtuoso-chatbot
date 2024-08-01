# Aero VR Tuoso

**Note: Luanch the servers first.**

### Stream Server
Requirements:
- OBS Studio
- Docker Container: illuspas/node-media-server

```docker run --name nms -d -p 1935:1935 -p 8000:8000 -p 8443:8443 illuspas/node-media-server```

**Configure OBS Studio**
- Go to File -> Settings -> Stream
- Fill the following parameters
  - Server: rtmp://localhost/live
  - Stream Key: STREAM_NAME
![alt text](./ReadMe%20Images/obs_configs.png)

### Redis Server
```cd ./redis && docker-compose up```

### Starting the Web App

**Installing Packages**
```npm install```

**Luanch Web App**
```npm run dev```

