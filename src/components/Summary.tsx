const Summary = (props) => {
  let date = new Date();
  let time = date.toTimeString().split(' ');

  return (
    <div className='flex flex-col justify-center gap-2'>
      <div className='flex flex-col gap-1'>
        <div className="flex gap-2">
          <p className='font-medium text-start'>{'Instruction'}</p>
          <p className='text-start text-gray-400'>{`(${time[0]})`}</p>
        </div>
        <p className='text-start'>{`${props.instruction}`}</p>
      </div>
      <div className='flex flex-col gap-1'>
        <div className="flex gap-2">
          <p className='font-medium text-start'>{'Response'}</p>
          <p className='text-start text-gray-400'>{`(${time[0]})`}</p>
        </div>
        <p className='text-start'>{`${props.response}`}</p>
      </div>
    </div>
  )
}

export default Summary
