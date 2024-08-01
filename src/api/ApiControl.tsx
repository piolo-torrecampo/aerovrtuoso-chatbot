import { useState } from 'react';

const GetResponse = async () => {
  const [data, setData] = useState(null);  

  try {
    const response = await fetch('http://localhost:8008/response'); // Replace with your API endpoint
    if (response.ok) {
      const json = await response.json();
      setData(json);
      return data;
    } else {
      console.log('Something went wrong');
    }
  } catch (error) {
    return error;
  }
}

export default GetResponse;