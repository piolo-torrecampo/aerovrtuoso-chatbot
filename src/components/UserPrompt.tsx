import { Separator } from "./ui/separator"
import { FaUnity, FaBrain, FaUser } from "react-icons/fa";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

interface UserInput {
  instruction: string;
  id: number;
  type: string;
  time: string;
}

const UserPrompt: React.FC<UserInput> = (props) => {
  let splitted_instruction
  let action
  let splitted_action

  if(props.instruction.includes("|")){
    splitted_instruction = props.instruction.split("|")
    splitted_action = splitted_instruction[0].split(":")
    action = splitted_action[0].split(" ")
  } else {
    splitted_instruction = [props.instruction]
  }
  
  return (
    <>
      {props.type == "fromUnity" ? (
        <div className='flex flex-col justify-start' key={props.id}>
          <AlertDialog>
            <AlertDialogTrigger>
              <div className="flex flex-row items-center gap-3 px-2">
                <p><FaUnity /></p>
                <p>{props.time}</p>
                <p>-</p>
                <p className='my-2 text-start'>{splitted_instruction[0]}</p>
              </div>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Summary</AlertDialogTitle>
                <AlertDialogDescription>
                  {splitted_instruction[0] && (
                    <div className="mb-4">
                      <h1 className="text-lg font-semibold text-gray-800">Status</h1>
                      {splitted_instruction[0]?.includes('successfully') ? (
                        <p className="text-base text-gray-600">Success.</p>
                      ) : (
                        <p className="text-base text-gray-600">Failed.</p>
                      )}
                    </div>
                  )}

                  {action[0] && (
                    <div className="mb-4">
                      <h1 className="text-lg font-semibold text-gray-800">Action</h1>
                      <p className="text-base text-gray-600">{action[0]}</p>
                    </div>
                  )}

                  {splitted_action[1] && (
                    <div className="mb-4">
                      <h1 className="text-lg font-semibold text-gray-800">Response</h1>
                      <p className="text-base text-gray-600">{splitted_action[1]}</p>
                    </div>
                  )}

                  {(splitted_instruction[1] || splitted_instruction[2]) && (
                    <div className="mb-4">
                      <h1 className="text-lg font-semibold text-gray-800">Object Status (X, Y, Z)</h1>
                      {splitted_instruction[1] && (
                        <p className="text-base text-gray-600">{splitted_instruction[1]}</p>
                      )}
                      {splitted_instruction[2] && (
                        <p className="text-base text-gray-600">{splitted_instruction[2]}</p>
                      )}
                    </div>
                  )}

                  {splitted_instruction[3] && (
                    <div className="mb-4">
                      <h1 className="text-lg font-semibold text-gray-800">JSON</h1>
                      <p className="text-base text-gray-600">{splitted_instruction[3]}</p>
                    </div>
                  )}
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Close</AlertDialogCancel>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
          <Separator />
        </div>
      ) : props.type == "fromUser" ? (
        <div className='flex flex-col justify-start' key={props.id}>
          <div className="flex flex-row items-center gap-3 px-2">
            <p><FaUser /></p>
            <p>{props.time}</p>
            <p>-</p>
            <p className='my-2 text-start'>{splitted_instruction[0]}</p>
          </div>
          <Separator />
        </div>
      ) : props.type == "fromLlm" ? (
        <div className='flex flex-col justify-start' key={props.id}>
          <div className="flex flex-row items-center gap-3 px-2">
            <p><FaBrain /></p>
            <p>{props.time}</p>
            <p>-</p>
            <p className='my-2 text-start'>{splitted_instruction[0]}</p>
          </div> 
          <Separator />
        </div>
      ) : (
        <div>
        </div>
      )}
    </>
  )
}

export default UserPrompt
