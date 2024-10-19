import React, { useState, useEffect, useRef } from 'react';
import UrlInput from './UrlInput';
import ProductTable from './ProductTable';
import SpinnerIcon from "./svg/SpinnerIcon.jsx";

const ProductApp = () => {
  const [statusMessage, setStatusMessage] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true); // State to toggle sidebar
  const [isInstructionsOpen, setIsInstructionsOpen] = useState(false); // State for instructions dropdown
  const socketRef = useRef(null);
  const loadingRef = useRef(null);
  /// const [currentLinkIndex, setCurrentLinkIndex] = useState(-1);
  /// const [totalNumLinks, setTotalNumLinks] = useState(0);
  const [currentLink, setCurrentLink] = useState('');
  const [scrapingStatus, setScrapingStatus] = useState('Not started');
  const [inferenceStatus, setInferenceStatus] = useState('Not started');

  const totalNumLinksRef = useRef(0);
  const currentLinkIndexRef = useRef(-1);


  const handleSubmit = async (formData) => {
    setIsLoading(true);
    totalNumLinksRef.current = formData.urls.length;

    setScrapingStatus('Not started.');
    setInferenceStatus('Not started.');

    loadingRef.current?.scrollIntoView({ behavior: 'smooth' });

    if (socketRef.current) {
      socketRef.current.send(
        JSON.stringify({
          links: formData.urls,
          scrape_subpages: formData.searchSubpages,
          custom_sitemap_tags: formData.customSitemapTags.split(","),
          wanted_words: formData.wantedWords.split(","),
        })
      );
    }
  };

  // This will be sent to the ProductTable component as a prop
  const handleClearClick = () => {
    console.log('Clearing results...');
    setResults([]);
    setIsLoading(false);
    setScrapingStatus('Not started.');
    setInferenceStatus('Not started.');
    setCurrentLink('');
    totalNumLinksRef.current = 0;
    currentLinkIndexRef.current = -1;
  }

  useEffect(() => {
    const socket = new WebSocket("ws://" + import.meta.env.VITE_ML_BACKEND_URL + "/ws/inference/");
    socketRef.current = socket;

    socket.onopen = () => {
      console.log('WebSocket connection established.');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.message) {
        setStatusMessage(data.message);
        console.log(data.message);
        if (data.message.startsWith("Iteration: ")) {
          console.log(data.message);
          const iterationIndex = parseInt(data.message.split(" ")[1]);
          const link = data.message.split(" ")[2];
          currentLinkIndexRef.current = iterationIndex;
          setCurrentLink(link);
        }

        if (data.message.startsWith("Scraping: ")) {
          setScrapingStatus(data.message);
        }

        if (data.message.startsWith("Inference: ")) {
          setInferenceStatus(data.message);
          console.log(totalNumLinksRef.current, currentLinkIndexRef.current);
          if (data.message === "Inference: Inference completed." && totalNumLinksRef.current <= currentLinkIndexRef.current) {
            console.log('Inference completed.');
            setIsLoading(false);
          }
        }
      } else if (data.product_name && data.link) {
        setResults((prevResults) => [
          ...prevResults,
          {
            product_name: data.product_name,
            product_price: data.product_price,
            product_img_urls: data.product_img_urls,
            link: data.link,
          },
        ]);
      }
    };

    socket.onclose = (event) => {
      console.log('WebSocket connection closed. Code:', event.code, 'Reason:', event.reason);
    };

    return () => {
      socketRef.current?.close();
    };
  }, []);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const toggleInstructions = () => {
    setIsInstructionsOpen(!isInstructionsOpen);
  };

  return (
    <div className="flex h-screen">
      <div className={`flex-1 ml-0 ${isSidebarOpen ? 'ml-[20%]' : ''} transition-all duration-300`}>
        <div className="p-4 mt-16 -ml-[30px]">
          {/* Loading Section */}
          <div ref={loadingRef} className="mt-4 mb-8">
            {isLoading && results.length === 0 && ( /// isLoading && only
              <div className="flex items-center justify-center space-x-4">
                <SpinnerIcon className="h-10 w-10 animate-spin" />
                <p className="text-xl text-gray-700 font-bold">Processing...</p>
              </div>
            )}
          </div>

          {/* Placeholder for results table */}
          {results.length === 0 && !isLoading && (
              <div className="flex items-center justify-center h-96">
              <p className="text-xl text-gray-700 font-bold ">Start searching for furniture in order to see results.</p>
              </div>
          )}

          {/* Product Table */}
          {results.length > 0 && <ProductTable products={results} onClearClick={handleClearClick} isLoading={isLoading} />}
        </div>
      </div>

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
