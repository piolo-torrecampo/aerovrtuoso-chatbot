import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "./ui/button";
import { Separator } from "@/components/ui/separator"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { LuMove3D } from "react-icons/lu";

interface UpdatedPrefabs {
  prefabs: string[];
  onSelectPrefab: (prefab: string) => void;
}

const PrefabList: React.FC<UpdatedPrefabs> = ({ prefabs, onSelectPrefab }) => {
  const handleButtonClick = (e) => {
    onSelectPrefab(e.target.value);
  };
  
  return (
    <ScrollArea className="h-96 rounded-md border">
      <div className="flex flex-col">
        {prefabs.length > 0 ? prefabs.map((item, index) => (
          <div key={index}>
            <div className='flex justify-between'>
              <Button 
                className="bg-white rounded-none text-black hover:bg-cyan-400 w-full" 
                onClick={handleButtonClick} 
                value={item}
                key={index}
              >{item}</Button>
              <Dialog>
                  <DialogTrigger className="bg-white rounded-none text-black hover:bg-cyan-400 p-2"><LuMove3D /></DialogTrigger>
                  <DialogContent>
                      <DialogHeader>
                      <DialogTitle>{item}</DialogTitle>
                      <DialogDescription>
                      </DialogDescription>
                      </DialogHeader>
                  </DialogContent>
              </Dialog>
            </div>
            <Separator />
          </div>
        )) :
          <div>
            <p>No objects found.</p>
            <Separator />
          </div>
        } 
      </div>
      <Separator />
    </ScrollArea>
  );
};

export default PrefabList;