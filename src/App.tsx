import './App.css'
import { useState, useEffect } from 'react';
import axios from "axios";
import PrefabList from './components/PrefabList';
import Logo from './components/Logo';
import StreamPlayer from './components/StreamPlayer';
// import Summary from './components/Summary';
import UserPrompt from './components/UserPrompt';

import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from './components/ui/button';
import { IoSend } from 'react-icons/io5';
import { Input } from './components/ui/input';

function App() {
  const [userInstruction, setUserInstruction] = useState('');
  const [prompts, setPrompts] = useState<object[]>([]);
  const [availablePrefabs, setAvailablePrefabs] = useState<string[]>([]);
  const [scenePrefabs, setScenePrefabs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [llmStatus, setLlmStatus] = useState(false)
  const [unityStatus, setUnityStatus] = useState(false)
  const responseUrl = "http://localhost:8008/response";
  const llmStatusUrl = "http://localhost:8008/llm_status";
  const llmUrl = "http://localhost:8009/set/prompt";


  useEffect(() => {
    const fetchData = async () => {
      if (!unityStatus) {
        try {
          // Fetch the first API (responseUrl)
          const response = await axios.get(responseUrl);
          const currentResponse = response.data.response; // Assign to the global variable

          if (currentResponse) {
            // Process the response
            const availablePrefabs = currentResponse.available_prefabs;
            const currentObjects = currentResponse.current_objects;

            setAvailablePrefabs(availablePrefabs.split(', '));
            setScenePrefabs(currentObjects.split(', '));

            const responseObj = {
              message: currentResponse.message,
              type: "fromUnity",
              timeStamp: new Date().toTimeString().split(' ')[0].toString(),
            };

            setUnityStatus(true);
            setPrompts([...prompts, responseObj]);
          }
        } catch (error) {
          console.error("Error fetching Unity data:", error);
        }
      }

      if (!llmStatus) {
        try {
          // Fetch the second API (llmStatusUrl)
          const status = await axios.get(llmStatusUrl);
          const llmStatusResponse = status.data.llmStatus;

          if (llmStatusResponse) {
            setLlmStatus(true);
          }
        } catch (error) {
          console.error("Error fetching LLM status:", error);
        }
      }
    };

    // Example of calling the fetchData function
    fetchData();

    // Set up polling (every 5 seconds)
    const interval = setInterval(fetchData, 5000);

    // To stop the interval when certain conditions are met
    clearInterval(interval);
  }, []);

  const handleUserInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUserInstruction(e.target.value);
  }

  const pastePrefabValue = (item: string) => {
    if(userInstruction[userInstruction.length-1] == ' ') {
      setUserInstruction(userInstruction + item.toString().trim());
    }else{
      setUserInstruction(userInstruction + item.toString());
    }
  }

  const handleSubmit = async (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (userInstruction.trim()) {
      setUserInstruction('');
      setLoading(true);

      const userPrompt = {
        message: userInstruction.trim(),
        type: "fromUser",
        timeStamp: new Date().toTimeString().split(' ')[0].toString()
      };
      
      setPrompts(prevPrompts => [...prevPrompts, userPrompt])

      try {
        await axios.post(llmUrl, { prompt : userInstruction.trim() })
          .then(response => {
            console.log(response)
            const parsedData = typeof response.data === 'string' ? JSON.parse(response.data) : response.data;
            console.log(parsedData);
            
            if (parsedData.response && parsedData.response.available_prefabs && parsedData.response.current_objects) {
              const availablePrefabs = parsedData.response.available_prefabs;
              const currentObjects = parsedData.response.current_objects;

              const splitAvailablePrefabs = availablePrefabs.split(', ');
              const splitCurrentObjects = currentObjects.split(', ');
              
              setAvailablePrefabs(splitAvailablePrefabs)
              setScenePrefabs(splitCurrentObjects);

              const responseObj = {
                message: parsedData.response.message,
                type: "fromUnity",
                timeStamp: new Date().toTimeString().split(' ')[0].toString()
              };

              setPrompts(prevPrompts => [...prevPrompts, responseObj]);
            } else {
              const responseObj = {
                message: parsedData.response.message,
                type: "fromLlm",
                timeStamp: new Date().toTimeString().split(' ')[0].toString()
              };

              setPrompts(prevPrompts => [...prevPrompts, responseObj]);
            }
          })
      } catch (error) {
        console.error("Error posting data:", error);
      } finally {
        setLoading(false); // Stop loading
      }
    }
  }

  const Spinner = () => (
    <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-white bg-opacity-75"></div>
  );

  const excludedKeywords = [
    'snap_point',
    'ray interactor',
    'poke interactor',
    'direct interactor',
    'left controller',
    'right controller',
    'dynamic move provider',
    'debug updater',
    'trackables',
    'hand',
    'Canvas',
    'Value',
    'Button',
    'XR',
    'UI',
    'Tools',
    'Text',
    'EventSystem',
    'Snap Point',
    'Parts',
    'Light',
    'Environment',
    'Menu',
    'Move',
    'Other',
    'Sfx',
    'Camera',
    'Manual',
    'Teleport',
    'Turn',
    'Ray',
    'Anchor',
    'Background',
    'Floor',
    'Image',
    'InitializeScripts',
    'Input Action Manager',
    'Locomotion System'
  ];
  
  const filteredScenePrefabs = scenePrefabs.filter(item =>
    !excludedKeywords.some(keyword => item.toLowerCase().includes(keyword.toLowerCase()))
  );
   
  return (
    <div className='grid grid-flow-row-dense grid-cols-12 grid-rows-12 gap-4 p-4 h-screen'>
      <Card className='col-span-3 row-span-12 p-4 shadow-md flex flex-col justify-between'>
        <CardHeader>
          <CardTitle><Logo /></CardTitle>
          <CardDescription>DESIGN OF A DYNAMIC SCENARIO-BASED VIRTUAL TRAINING SIMULATION FOR SMALL AIRCRAFT ENGINE MAINTENANCE</CardDescription>
          <CardDescription>Unity: { unityStatus ? 'Connected' : 'Loading...'}</CardDescription>
          <CardDescription>LLM: { llmStatus ? 'Connected' : 'Loading...'}</CardDescription>
        </CardHeader>
        <CardContent className='flex justify-center w-full'>
          <Tabs defaultValue="scene" className="w-full">
            <TabsList className='w-full'>
              <TabsTrigger className='w-full' value="available">Available</TabsTrigger>
              <TabsTrigger className='w-full' value="scene">Scene</TabsTrigger>
            </TabsList>
            <TabsContent value="available">
              <PrefabList prefabs={availablePrefabs.sort()} onSelectPrefab={pastePrefabValue} />
            </TabsContent>
            <TabsContent value="scene">
              <PrefabList prefabs={filteredScenePrefabs.sort()} onSelectPrefab={pastePrefabValue} />
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
      <Card className='col-span-9 row-span-4 p-2 shadow-md flex flex-col gap-2'>
        <div className='flex flex-row justify-center gap-x-2'>
          <Input  className="h-12" id="inputbox" placeholder='Enter your instruction here here.' value={userInstruction} onChange={handleUserInput}/>
          <Button className='h-12 w-12' onClick={handleSubmit}>
            {
              loading ? <Spinner /> : <IoSend />
            }
          </Button>
        </div>
        <ScrollArea className='h-full overflow-auto'>
          {
            prompts.slice().reverse().map((item, key) => {
              return <UserPrompt id={item.timeStamp} time={item.timeStamp} instruction={item.message} type={item.type}/>
            })
          }
        </ScrollArea>
      </Card>
      {/*<Card className='col-span-4 row-span-4 p-2 shadow-md'>
        <CardHeader>
          <CardTitle>SUMMARY</CardTitle>
        </CardHeader>
        <Summary instruction="Sample" response="The quick brown fox jumps over the lazy dogumps over the lazy dog."/>
      </Card>*/}
    </div>
  )
}

export default App
