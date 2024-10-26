# Aero VR Tuoso - Chatbot

**Project Name**: Design of a Dynamic Scenario-Based Virtual Training Simulation for Small Aircraft Engine Maintenance
**Description**: The project design aims to design an algorithm based on the Large Language Model (LLM) in a dynamic scenario generation for Virtual Reality (VR) that will be utilized by the aircraft maintenance trainees.

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


## API END POINTS

#### TABLE OF CONENTS
- [insert](#insert)
- [scale](#scale)
- [rotation](#rotation)
- [remove](#remove)
- [replace](#replace)

### INSERT
Insert is a the tool for inserting object.
```
{
    "prompt": "Insert a Sphere at the left side of the Cube",
    "action": "insert",
    "parameters": {
        "reference_object": "Cube",
        "prefab": "Sphere",
        "direction": "front",
        "value": "1"
    }
}
```
#### Parameters
Name | Data Type | Descriptions
| -- | -- | -- | 
prompt | string | prompt of the user
action | string | action performed by unity
prefab | string | 3d object name
reference_object | string | reference object for the inserted object
direction | string | direction of the placement of inserted object
value | float | distance between the reference object

### SCALE
Scale is a the tool for making the object bigger.
```
{
    "prompt": "Double the scale of the workbench",
    "action": "scale",
    "parameters": {
        "prefab": "workbench",
        "axis": "all", "x", // x, y, z, all, increase, decrease
        "value": "2" // no limit
    }
}
```
#### Parameters
Name | Data Type | Description
| -- | -- | -- | 
prompt | string | prompt of the user
action | string | action performed by unity
prefab | string | 3d object name
axis | string | target axis to scale
value | float | number of units to be applied for scaling

### ROTATION
This tool allows to rotate specific object in the scene.
```
{
    "prompt": "Rotate the workbench at 45 degrees in z axis",
    "action": "rotate",
    "parameters": {
        "prefab": "workbench",
        "axis": "z", // x, y, z
        "value": "45" // -360 to 360
    }
}
```
#### Parameters
Name | Data Type | Description
| -- | -- | -- | 
prompt | string | prompt of the user
action | string | action performed by unity
prefab | string | 3d object name
axis | string | target axis to rotate
value | float | degrees of rotation

### REMOVE
This tool allows to remove a specific object in the scene.
```
{
    "prompt": "Romeve workbench",
    "action": "remove",
    "parameters": {
        "prefab": "workbench",
        "value": "1" // can be any number
    }  
}
```
#### Parameters
Name | Data Type | Description
| -- | -- | -- | 
prompt | string | prompt of the user
action | string | action performed by unity
prefab | string | 3d object tag name
value | float | quantity of the 3d object/s that will be remove

### REPLACE
This tool allows to replace a specific object in the scene and put another object in the same place.
```
{
    "prompt": "Replace the cube to workbench",
    "action": "replace",
    "parameters": {
        "prefab": "Cube",
        "object_to_replace": "workbench"
    }   
}
```
#### Parameters
Name | Data Type | Description
| -- | -- | -- | 
prompt | string | prompt of the user
action | string | action performed by unity
prefab | string | 3d object name under resources folder
object_to_replace | string| name of old object

### MOVE
This tool allows to move a specific object in the scene. 
```
{
    "prompt": "Move the workbench to the right",
    "action": "move",
    "parameters": {
        "prefab": "workbench",
        "direction": "right", // top, left, right, bottom, front, back
        "value": "1"
    }
}
```
#### Parameters
Name | Data Type | Description
| -- | -- | -- | 
prompt | string | prompt of the user
action | string | action performed by unity
prefab | string | 3d object name under resources folder
direction | string | direction of the next movement of the object
object_to_replace | string| name of old object

