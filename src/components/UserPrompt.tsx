import { Separator } from "./ui/separator"
import { FaUnity, FaBrain, FaUser } from "react-icons/fa";

interface UserInput {
  instruction: string;
  id: number;
  type: string;
  time: string;
}

const UserPrompt: React.FC<UserInput> = (props) => {
  return (
    <>
      {props.type == "fromUnity" ? (
        <div className='flex flex-col justify-start' key={props.id}>
          <div className="flex flex-row items-center gap-3 px-2">
            <p><FaUnity /></p>
            <p>{props.time}</p>
            <p>-</p>
            <p className='my-2 text-start'>{props.instruction}</p>
          </div>
          <Separator />
        </div>
      ) : props.type == "fromUser" ? (
        <div className='flex flex-col justify-start' key={props.id}>
          <div className="flex flex-row items-center gap-3 px-2">
            <p><FaUser /></p>
            <p>{props.time}</p>
            <p>-</p>
            <p className='my-2 text-start'>{props.instruction}</p>
          </div>
          <Separator />
        </div>
      ) : props.type == "fromLlm" ? (
        <div className='flex flex-col justify-start' key={props.id}>
          <div className="flex flex-row items-center gap-3 px-2">
            <p><FaBrain /></p>
            <p>{props.time}</p>
            <p>-</p>
            <p className='my-2 text-start'>{props.instruction}</p>
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
