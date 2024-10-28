import React, { useState, useEffect, useRef } from 'react';
import UrlInput from './UrlInput';
import ProductTable from './ProductTable';
import SpinnerIcon from "./svg/SpinnerIcon.jsx";

// main component
const ProductApp = () => {
  const [statusMessage, setStatusMessage] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true); // State to toggle sidebar
  const [isInstructionsOpen, setIsInstructionsOpen] = useState(false); // State for instructions dropdown
  const [currentLink, setCurrentLink] = useState('');
  const [scrapingStatus, setScrapingStatus] = useState('Not started');
  const [inferenceStatus, setInferenceStatus] = useState('Not started');

  const socketRef = useRef(null); // websocket reference for the connection (should not be a state)
  const loadingRef = useRef(null); // same here
  const totalNumLinksRef = useRef(0); // reference to the total number of links to scrape ( for status bar )
  const currentLinkIndexRef = useRef(-1); // reference to the current link index ( for status bar )

  // all the logic for handling the form submission and websocket connection
  const handleSubmit = async (formData) => {
    setIsLoading(true);
    totalNumLinksRef.current = formData.urls.length;

    setScrapingStatus('Not started.');
    setInferenceStatus('Not started.');

    loadingRef.current?.scrollIntoView({ behavior: 'smooth' });

    if (socketRef.current) { // if we are connected to the websocket
      socketRef.current.send( // send the form data to the backend
        JSON.stringify({
          links: formData.urls, // the URLs to scrape
          scrape_subpages: formData.searchSubpages, // whether to scrape subpages
          custom_sitemap_tags: formData.customSitemapTags.split(","), // custom sitemap tags
          wanted_words: formData.wantedWords.split(","), // wanted words
        })
      );
    }
  };

  // this will be sent to the ProductTable component as a prop to clear the results
  // its located here since I need multiple components to be able to perform actions accordingly
  const handleClearClick = () => {
    setResults([]);
    setIsLoading(false);
    setScrapingStatus('Not started.');
    setInferenceStatus('Not started.');
    setCurrentLink('');
    totalNumLinksRef.current = 0;
    currentLinkIndexRef.current = -1;
  }

  useEffect(() => {
    // create a new websocket connection to the backend endpoint (/ws/inference/)
    const socket = new WebSocket("ws://" + import.meta.env.VITE_ML_BACKEND_URL + "/ws/inference/");
    socketRef.current = socket; // store the reference in the ref

    socket.onopen = () => {
      console.log('WebSocket connection established.');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.message) { // if the message is a status message
        setStatusMessage(data.message); // set the status message
        if (data.message.startsWith("Iteration: ")) { // if the message is an iteration message
          const iterationIndex = parseInt(data.message.split(" ")[1]); // we update the current link index
          const link = data.message.split(" ")[2]; // we get the current link (by convention the link is the second word in the message - see the backend message format)
          currentLinkIndexRef.current = iterationIndex;
          setCurrentLink(link);
        }

        if (data.message.startsWith("Scraping: ")) { // if the message is a scraping status message
          setScrapingStatus(data.message);
        }

        if (data.message.startsWith("Inference: ")) { // if the message is an inference status message
          setInferenceStatus(data.message);
          if (data.message === "Inference: Inference completed." && totalNumLinksRef.current <= currentLinkIndexRef.current) { // if the number of links is equal to the current link index
            setIsLoading(false);
          }
        }
      } else if (data.product_name && data.link) { // we got data to add to the results
        setResults((prevResults) => [
          ...prevResults, // keep the previous results
          {
            product_name: data.product_name, // add the product data to the results
            product_price: data.product_price, // add the product data to the results
            product_img_urls: data.product_img_urls, // add the product data to the results
            link: data.link, // add the product data to the results
          },
        ]);
      }
    };

    socket.onclose = (event) => { // when the connection is closed
      console.log('WebSocket connection closed. Code:', event.code, 'Reason:', event.reason);
    };

    return () => {
      socketRef.current?.close(); // close the connection when the component is unmounted
    };
  }, []);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen); // toggle the sidebar
  };

  const toggleInstructions = () => {
    setIsInstructionsOpen(!isInstructionsOpen); // toggle the instructions dropdown
  };

  return (
    <div className="flex h-screen">
      <div className={`flex-1 ml-0 ${isSidebarOpen ? 'ml-[20%]' : ''} transition-all duration-300`}>
        <div className="p-4 mt-16 -ml-[30px]">
          {/* loading Section */}
          <div ref={loadingRef} className="mt-4 mb-8">
            {isLoading && results.length === 0 && ( /// isLoading && only if there are no results
              <div className="flex items-center justify-center space-x-4">
                <SpinnerIcon className="h-10 w-10 animate-spin" />
                <p className="text-xl text-gray-700 font-bold">Processing...</p>
              </div>
            )}
          </div>

          {/* placeholder for results table */}
          {results.length === 0 && !isLoading && (
              <div className="flex items-center justify-center h-96">
                {inferenceStatus !== 'Not started.' &&
                <p className="text-xl text-gray-700 font-bold ">No results found for your given link, please try again !</p>
                }
                {/* placeholder for results table if nothing is found */}
                {inferenceStatus === 'Not started.' &&
                <p className="text-xl text-gray-700 font-bold ">Start searching for furniture in order to see results.</p>
                }
              </div>
          )}

          {/* product Table */}
          {results.length > 0 && <ProductTable products={results} onClearClick={handleClearClick} isLoading={isLoading} />}
        </div>
      </div>


      {/* URL input */}
      <UrlInput
        onSubmit={handleSubmit}
        isSidebarOpen={isSidebarOpen}
        toggleSidebar={toggleSidebar}
        isInstructionsOpen={isInstructionsOpen}
        toggleInstructions={toggleInstructions}
        scrapingStatus={scrapingStatus}
        inferenceStatus={inferenceStatus}
        currentLinkIndex={currentLinkIndexRef.current}
        totalNumLinks={totalNumLinksRef.current}
        isLoading={isLoading}
        currentLink={currentLink}
      />
    </div>
  );
};

export default ProductApp;
