import {ReactFlvPlayer} from 'react-flv-player';

const StreamPlayer = () => {
  return (
    <ReactFlvPlayer
        url = "http://localhost:8000/live/STREAM_NAME.flv"
        className="absolute top-0 left-0 w-full h-full"
        width = "105vh"
        enableStashBuffer={true}
        hasVideo={true}
        isLive={true}
        isMuted={true}
        handleError={(err: string) => {
            switch (err) {
            case 'NetworkError':
                console.log('network error');
            break;
            case 'MediaError':
                console.log('network error');
            break;
            default:
                console.log('other error');
            }
        }}
    />
  )
}

export default StreamPlayer
