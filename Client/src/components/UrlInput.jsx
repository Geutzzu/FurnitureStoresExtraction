import React, { useState } from "react";
import InstructionsDropdown from "./InstructionsDropdown.jsx";
import Papa from "papaparse";

const SpinnerIcon = ({ className }) => (
  <svg className={`animate-spin ${className}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
  </svg>
);

const CheckIcon = ({ className }) => (
  <svg className={`text-green-500 ${className}`} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
    <path
      fillRule="evenodd"
      d="M10 18a8 8 0 100-16 8 8 0 000 16zm-1.5-8.9l4.8-4.9 1.4 1.5-6.2 6.3L5.5 9.1l1.4-1.4 1.6 1.6z"
      clipRule="evenodd"
    />
  </svg>
);


const UrlInput = ({
  onSubmit,
  isSidebarOpen,
  toggleSidebar,
  isInstructionsOpen,
  toggleInstructions,
  scrapingStatus,
  inferenceStatus,
  currentLinkIndex,
  totalNumLinks,
  isLoading,
  currentLink
}) => {
  const [url, setUrl] = useState("");  // Single URL input
  const [customSitemapTags, setCustomSitemapTags] = useState("");
  const [wantedWords, setWantedWords] = useState("");
  const [searchSubpages, setSearchSubpages] = useState(false);
  const [csvUrls, setCsvUrls] = useState([]);  // Array for URLs extracted from CSV
  const [csvFileName, setCsvFileName] = useState("");  // To display uploaded file name

  const handleSubmit = async (e) => {
    e.preventDefault();


    const formData = {
      urls: csvUrls.length > 0 ? csvUrls : [url],
      customSitemapTags: searchSubpages ? customSitemapTags : "",
      wantedWords: searchSubpages ? wantedWords : "",
      searchSubpages,
    };
    onSubmit(formData);
  };

  const handleCsvUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      Papa.parse(file, {
        complete: (result) => {
          const urls = result.data[0];
          setCsvUrls(urls);
          setCsvFileName(file.name);
        },
        error: (error) => {
          console.error("Error parsing CSV file:", error);
        }
      });
    }
  };

  const handleFileRemove = () => {
    setCsvUrls([]);
    setCsvFileName("");
  };

  return (
    <div className={`fixed top-0 left-0 h-full bg-white shadow-lg transform transition-transform duration-300 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} w-[20%] min-w-[250px]`}>
      <div className="relative">
        {/* Open/Close Sidebar Button */}
        <button
          className="bg-blue-500 text-white px-4 py-2 absolute right-[-40px] top-4 transform -rotate-90 "
          onClick={toggleSidebar}
        >
          {isSidebarOpen ? "Close" : "Open"}
        </button>

        {/* InstructionsDropdown Button */}
        <div className="absolute top-16 right-[-40px] mr-4 mt-3">
          <InstructionsDropdown
            isInstructionsOpen={isInstructionsOpen}
            toggleInstructions={toggleInstructions}
          />
        </div>
      </div>

      <div className="p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">
          Search for Furniture
        </h2>
        <form onSubmit={handleSubmit}>
          {/* Single URL input */}
          <div className="mb-6">
            <label className="block text-gray-700 mb-2" htmlFor="urlInput">
              Website URL:
            </label>
            <input
              type="url"
              id="urlInput"
              placeholder="https://myfurniture.com/furniture"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full p-2 border rounded"
              required={!csvUrls.length}  // Required only if no CSV is uploaded
              disabled={csvUrls.length > 0}  // Disable if a CSV file is uploaded
            />
          </div>

          <div className={`justify-center flex align-center`}>
            <p className="text-gray-700 mb-2 align-center">OR</p>
          </div>

          {/* File input for CSV upload with SVG icon and remove option */}
          <div className="mb-6">
            <label className="block text-gray-700 mb-2" htmlFor="csvInput">
              Upload CSV with URLs:
            </label>
            <div className="relative w-full p-2 border border-gray-300 rounded flex items-center justify-center cursor-pointer">
              <input
                type="file"
                id="csvInput"
                accept=".csv"
                onChange={handleCsvUpload}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <span className="text-gray-500">{csvFileName ? csvFileName : "Choose a CSV file"}</span>
            </div>
            {csvFileName && (
              <div className="mt-2 flex justify-between items-center">
                <p className="text-sm text-gray-500">Uploaded: {csvFileName}</p>
                <button
                  type="button"
                  onClick={handleFileRemove}
                  className="text-red-500 hover:underline text-sm"
                >
                  Remove File
                </button>
              </div>
            )}
          </div>

          {/* Checkbox to search subpages */}
          <div className="mb-6 flex items-center">
            <input
              type="checkbox"
              checked={searchSubpages}
              onChange={() => setSearchSubpages(!searchSubpages)}
              className="mr-3"
            />
            <label className="text-gray-700">Search subpages for furniture</label>
          </div>

          {/* Conditional inputs for sitemap tags and custom paths */}
          {searchSubpages && (
            <>
              <div className="mb-6">
                <label className="block text-gray-700 mb-2" htmlFor="wantedWordsInput">
                  Custom Paths in URLs (Optional):
                </label>
                <input
                  type="text"
                  id="wantedWordsInput"
                  placeholder="Enter custom paths separated by commas"
                  value={wantedWords}
                  onChange={(e) => setWantedWords(e.target.value)}
                  className="w-full p-2 border rounded"
                />
              </div>

              <div className="mb-6">
                <label className="block text-gray-700 mb-2" htmlFor="customSitemapTagsInput">
                  Custom XML Tags (Optional):
                </label>
                <input
                  type="text"
                  id="customSitemapTagsInput"
                  placeholder="Enter custom tags separated by commas"
                  value={customSitemapTags}
                  onChange={(e) => setCustomSitemapTags(e.target.value)}
                  className="w-full p-2 border rounded"
                />
              </div>
            </>
          )}

          <button
              type="submit"
              className={`bg-blue-500 text-white w-full py-2 rounded ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              disabled={isLoading}
          >
            {csvUrls.length > 0 ? "Search Multiple Furniture Sites" : "Search Furniture"}
          </button>
        </form>
      </div>

      {/* Current Status Display */}
      {currentLinkIndex > -1 &&  (
          <div className="p-4 border-t mt-4 bg-gray-50 rounded-lg shadow-lg">
            <h3 className="font-semibold text-gray-900 text-lg mb-2">Processing Status</h3>

            <div className="mb-4 flex items-center">
              <h4 className="text-sm font-semibold text-gray-700 mr-2">Link {currentLinkIndex} of {totalNumLinks}:</h4>
              <span className="text-xs text-gray-500">
                {currentLink.length > 45 ? `${currentLink.slice(0, 45)}...` : currentLink}
              </span>
            </div>

            <div className="mb-4 flex items-center">
              <h4 className="text-sm font-semibold text-gray-700 mr-2">Scraping Status:</h4>
            {(scrapingStatus === "Scraping: Scraping completed." || !searchSubpages) ? (
              <CheckIcon className="h-5 w-5 text-green-500" aria-hidden="true" />
            ) : (
              <SpinnerIcon className="h-5 w-5 text-blue-500" aria-hidden="true" />
            )}
            <span className="text-xs text-gray-500 ml-2">{!searchSubpages ? "Skipped." : scrapingStatus.replace("Scraping:", "")}</span>
          </div>

          <div className="flex items-center">
            <h4 className="text-sm font-semibold text-gray-700 mr-2">Inference Status:</h4>
            {inferenceStatus === "Inference: Inference completed." ? (
              <CheckIcon className="h-5 w-5 text-green-500" aria-hidden="true" />
            ) : (
              <SpinnerIcon className="h-5 w-5 text-blue-500" aria-hidden="true" />
            )}
            <span className="text-xs text-gray-500 ml-2">{inferenceStatus.replace("Inference:", "")}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default UrlInput;
