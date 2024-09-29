import React, { useState, useEffect, useRef } from 'react';
import UrlInput from "./UrlInput.jsx";
import ProductTable from "./ProductTable.jsx";

const ProductApp = () => {
    const [statusMessage, setStatusMessage] = useState('');
    const [results, setResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const socketRef = useRef(null); // Use useRef to keep track of WebSocket

    const handleSubmit = async (formData) => {
        setResults([]);
        if (socketRef.current) {
            // Send data via the WebSocket if already open
            socketRef.current.send(JSON.stringify({
                link: formData.url,
                scrape_subpages: formData.searchSubpages,
                custom_sitemap_tags: formData.customSitemapTags.split(","),
                wanted_words: formData.wantedWords.split(",")
            }));
        }
        setIsLoading(true);
    };

    useEffect(() => {
            console.log("Results updated in ProductApp: ", results);
            }, [results]);
    // This useEffect will handle opening and maintaining the WebSocket connection
    useEffect(() => {
        // Open a WebSocket connection
        const socket = new WebSocket("ws://" + import.meta.env.VITE_ML_BACKEND_URL + "/ws/inference/");
        socketRef.current = socket; // Store socket in ref to reuse it across renders

        // Handle WebSocket connection open event
        socket.onopen = () => {
            console.log('WebSocket connection established.');
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.message) {
                setStatusMessage(data.message);
                setIsLoading(statusMessage.includes("Inference: Inference completed."));
                console.log("Status message: ", data.message);
            }
            else if (data.product_name && data.link) {
                setResults((prevResults) => [
                    ...prevResults,
                    {
                        product_name: data.product_name,
                        product_price: data.product_price,
                        product_img_urls: data.product_img_urls,
                        link: data.link,
                    }
                ]);
            }
        };


        socket.onclose = (event) => {
            console.log('WebSocket connection closed. Code:', event.code, 'Reason:', event.reason);
        };

        return () => {
            if (socketRef.current) {
                socketRef.current.close();
                console.log("WebSocket connection closed (component unmounted)");
            }
        };
    }, []); // Empty dependency array ensures the WebSocket connection is established only once


    return (
        <div className="min-h-screen flex flex-col justify-center items-center bg-gray-100">
            <UrlInput onSubmit={handleSubmit} />

            {isLoading && (
                <div className="flex flex-col justify-center items-center mt-10">
                    <svg
                        className="animate-spin h-12 w-12 text-blue-500"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                    >
                        <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                        ></circle>
                        <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                        ></path>
                    </svg>
                    <p className="mt-4 text-lg text-gray-700">{statusMessage}</p>
                </div>
            )}

            {results.length > 0 && (
                <ProductTable products={results} />
            )}
        </div>
    );
};

export default ProductApp;
