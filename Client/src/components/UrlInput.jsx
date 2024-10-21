import React, { useState } from "react";
import InstructionsDropdown from "./InstructionsDropdown.jsx";
import Papa from "papaparse";
import CheckIcon from "./svg/CheckIcon.jsx";
import SpinnerIcon from "./svg/SpinnerIcon.jsx";
import CloseIcon from "./svg/CloseIcon.jsx";
import MenuIcon from "./svg/MenuIcon.jsx";
import UploadIcon from "./svg/UploadIcon.jsx";


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
  const [url, setUrl] = useState("");  // single URL input
  const [customSitemapTags, setCustomSitemapTags] = useState("");
  const [wantedWords, setWantedWords] = useState("");
  const [searchSubpages, setSearchSubpages] = useState(false);
  const [csvUrls, setCsvUrls] = useState([]);  // array for URLs extracted from CSV
  const [csvFileName, setCsvFileName] = useState("");  // to display uploaded file name

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

  // function to handle CSV file upload using PapaParse library
  const handleCsvUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setCsvFileName(file.name);
      setCsvUrls([]);
      Papa.parse(file, {
        complete: (result) => {
          for (let i = 0; i < result.data.length; i++) {
            const url = result.data[i][0];
            if (url) {
              setCsvUrls((prev) => [...prev, url]);
            }
          }
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
    <div className={`fixed top-0 left-0 h-full bg-white shadow-lg transform transition-transform border-r-1 border-darkGraphite duration-300 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} w-[20%] min-w-[250px]`}>
      <div className="relative">
        {/* Open/Close Sidebar Button */}
        <button
          className="bg-darkGraphite text-white px-2 py-2 absolute right-[-40px] top-6 transform hover:opacity-90 rounded"
          onClick={toggleSidebar}
        >
          {isSidebarOpen ?  <CloseIcon className="h-5 w-5" /> : <MenuIcon className="h-5 w-5" /> }
        </button>

        {/* InstructionsDropdown Button */}
        <div className="absolute top-16 right-[-40px] mt-3">
          <InstructionsDropdown
            isInstructionsOpen={isInstructionsOpen}
            toggleInstructions={toggleInstructions}
          />
        </div>
      </div>

      <div className=" flex justify-between flex-col h-full flex-grow">
        <div className="p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Search for Furniture
          </h2>
          <form onSubmit={handleSubmit}>
            {/* single URL input */}
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
                  required={!csvUrls.length}  // required only if no CSV is uploaded
                  disabled={csvUrls.length > 0 || isLoading}  // disable if a CSV file is uploaded
              />
            </div>

            <div className={`justify-center flex align-center`}>
              <p className="text-gray-700 mb-2 align-center">OR</p>
            </div>

            {/* file input for CSV upload with SVG icon and remove option */}
            <div className="mb-6">
              <label className="block text-gray-700 mb-2" htmlFor="csvInput">
                Upload CSV with URLs:
              </label>
              <div
                  className="relative w-full p-2 border border-gray-300 rounded flex items-center justify-center cursor-pointer">
                <input
                    type="file"
                    id="csvInput"
                    accept=".csv"
                    onChange={handleCsvUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    disabled={isLoading}
                />
                <UploadIcon className="h-6 w-6 text-gray-500 mr-2" />
                <span className="text-gray-500">{csvFileName ? csvFileName : "Upload a CSV file"}</span>
              </div>
              {csvFileName && (
                  <div className="mt-2 flex justify-between items-center">
                    <p className="text-sm text-gray-500">Uploaded: {csvFileName}</p>
                    <button
                        type="button"
                        onClick={handleFileRemove}
                        className="text-gray-500 underline hover:text-gray-900 text-sm"
                    >
                      Remove File
                    </button>
                  </div>
              )}
            </div>

            {/* checkbox to search subpages */}
            <div className="mb-6">
              <input
                  type="checkbox"
                  checked={searchSubpages}
                  onChange={() => setSearchSubpages(!searchSubpages)}
                  className="mr-3"
                  disabled={isLoading}

              />
              <label className="text-gray-700">Search subpages for furniture</label>
            </div>

            {/* inputs for sitemap tags and custom paths */}
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
                        disabled={isLoading}
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
                        disabled={isLoading}
                    />
                  </div>
                </>
            )}

            <button
                type="submit"
                className={`bg-darkGraphite text-white w-full py-2 rounded hover:opacity-90 ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                disabled={isLoading}
            >
              {csvUrls.length > 0 ? "Search Multiple Furniture Sites" : "Search Furniture"}
            </button>
          </form>
        </div>

        {/* processing status bar*/}
      {currentLinkIndex > -1 && (
          <div className="p-4 border-t mt-4 bg-gray-50 shadow-lg">
            <div className="flex items-center mb-4">
              <h3 className="font-semibold text-gray-900 text-lg mb-1 mr-3">Processing Status</h3>
              {isLoading ? (<SpinnerIcon className="h-5 w-5" aria-hidden="true"/>) : (
                    <CheckIcon className="h-5 w-5 text-green-500" aria-hidden="true"/>
                )}
            </div>
            <div className="mb-4 flex items-center">
            <h4 className="text-sm font-semibold text-gray-700 mr-2">Link {currentLinkIndex} of {totalNumLinks}:</h4>
              <span className="text-xs text-gray-500">
                {currentLink.length > 35 ? `${currentLink.slice(0, 35)}...` : currentLink}
              </span>
            </div>

            <div className="mb-4 flex items-center">
              <h4 className="text-sm font-semibold text-gray-700 mr-2">Scraping Status:</h4>
              {(scrapingStatus === "Scraping: Scraping completed." || (!searchSubpages || !isLoading)) ? (
                  <CheckIcon className="h-5 w-5 text-green-500" aria-hidden="true"/>
              ) : (
                  <SpinnerIcon className="h-5 w-5 text-darkColor" aria-hidden="true"/>
              )}
              <span
                  className="text-xs text-gray-500 ml-2">{(!searchSubpages || !isLoading) ? "Skipped." : scrapingStatus.replace("Scraping:", "")}</span>
            </div>

            <div className="flex items-center">
              <h4 className="text-sm font-semibold text-gray-700 mr-2">Inference Status:</h4>
              {inferenceStatus === "Inference: Inference completed." ? (
                  <CheckIcon className="h-5 w-5 text-green-500" aria-hidden="true"/>
              ) : (
                  <SpinnerIcon className="h-5 w-5" aria-hidden="true"/>
              )}
              <span className="text-xs text-gray-500 ml-2">{inferenceStatus.replace("Inference:", "")}</span>
            </div>
          </div>
      )}

      </div>
    </div>
  );
};

export default UrlInput;
