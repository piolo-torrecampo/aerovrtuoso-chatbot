import './App.css'
import { useState, useEffect } from 'react';
import axios from "axios";
import PrefabList from './components/PrefabList';
import Logo from './components/Logo';
import { Button } from './components/ui/button';
import { IoSend } from 'react-icons/io5';
import { Input } from './components/ui/input';
import StreamPlayer from './components/StreamPlayer';
import Summary from './components/Summary';
import UserPrompt from './components/UserPrompt';
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';


function App() {
  const [userInstruction, setUserInstruction] = useState('');
  const [prompts, setPrompts] = useState<object[]>([]);
  const [availablePrefabs, setAvailablePrefabs] = useState<string[]>([]);
  const [scenePrefabs, setScenePrefabs] = useState<string[]>([]);
  const [message, setMessage] = useState(null);
  const reponseUrl = "http://localhost:8008/response";

  let date = new Date();
  let time = date.toTimeString().split(' ');

  useEffect(() => {
    axios.get(reponseUrl).then((response) => {
      const currentReponse = response.data.response
      setMessage(currentReponse.message);

      const splittedAvailablePrefabs = currentReponse.available_prefabs.split(',')
      const splittedCurrentPrefabs = currentReponse.current_object.split(',')

      setAvailablePrefabs(splittedAvailablePrefabs);
      setScenePrefabs(splittedCurrentPrefabs);

      const reponseObj = {
        message: currentReponse.message,
        type: "fromUnity",
        timeStamp: time[0].toString()
      }

      if (message != null) {
        setPrompts([...prompts, reponseObj]);
      }
    })
  }, [])

  const handleUserInput = (e) => {
    setUserInstruction(e.target.value);
  }

  const pastePrefabValue = (item) => {
    if(userInstruction[userInstruction.length-1] == ' ') {
      setUserInstruction(userInstruction + item.toString().trim());
    }else{
      setUserInstruction(userInstruction + item.toString());
    }
    
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    if (userInstruction.trim()) {
      const userPrompt = {
        message: userInstruction.trim(),
        type: "fromUser",
        timeStamp: time[0].toString()
      }
      setPrompts([...prompts, userPrompt]);
      setUserInstruction('');
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  const excludedKeywords = [
    'snap_point',
    'ray interactor',
    'poke interactor',
    'direct interactor',
    'left controller',
    'right controller',
    'dynamic move provider',
    'debug updater',
    'trackables'
  ];
  
  const filteredScenePrefabs = scenePrefabs.filter(item =>
    !excludedKeywords.some(keyword => item.toLowerCase().includes(keyword))
  );
   
  return (
    <div className='grid grid-flow-row-dense grid-cols-12 grid-rows-12 gap-4 p-4 h-screen'>
      <Card className='col-span-3 row-span-12 p-4 shadow-md flex flex-col justify-between'>
        <CardHeader>
          <CardTitle><Logo /></CardTitle>
          <CardDescription>DESIGN OF A DYNAMIC SCENARIO-BASED VIRTUAL TRAINING SIMULATION FOR SMALL AIRCRAFT ENGINE MAINTENANCE</CardDescription>
        </CardHeader>
        <CardContent className='flex justify-center w-full'>
          <Tabs defaultValue="scene" className="w-full">
            <TabsList className='w-full'>
              <TabsTrigger className='w-full' value="available">Available</TabsTrigger>
              <TabsTrigger className='w-full' value="scene">Scene</TabsTrigger>
            </TabsList>
            <TabsContent value="available">
              <PrefabList prefabs={availablePrefabs} onSelectPrefab={pastePrefabValue} />
            </TabsContent>
            <TabsContent value="scene">
              <PrefabList prefabs={filteredScenePrefabs} onSelectPrefab={pastePrefabValue} />
            </TabsContent>
          </Tabs>
        </CardContent> 
        <CardFooter>
          © 2024 VR Worx
        </CardFooter>
      </Card>
      <Card className='col-span-9 row-span-8 p-4 shadow-md'>
        <CardContent className='flex justify-center w-full'>
          <div className='flex justify-center overflow-auto'>
            <StreamPlayer />
          </div>
        </CardContent>
      </Card>
      <Card className='col-span-5 row-span-4 p-2 shadow-md flex flex-col gap-2'>
        <div className='flex flex-row justify-center gap-x-2'>
          <Input  className="h-12" id="inputbox" placeholder='Enter your instruction here here.' value={userInstruction} onChange={handleUserInput} onKeyDown={handleKeyPress}/>
          <Button className='h-12 w-12' onClick={handleSubmit}><IoSend /></Button>
        </div>
        <ScrollArea className='h-full overflow-auto'>
          {
            prompts.slice().reverse().map((item, key) => {
              return <UserPrompt key={key} time={item.timeStamp} instruction={item.message} type={item.type} />
            })
          }
        </ScrollArea>
      </Card>
      <Card className='col-span-4 row-span-4 p-2 shadow-md'>
        <CardHeader>
          <CardTitle>SUMMARY</CardTitle>
        </CardHeader>
        <Summary instruction="Sample" response="The quick brown fox jumps over the lazy dogumps over the lazy dog."/>
      </Card>
    </div>
  )
}

export default App
