import React, { useState } from "react";
import InstructionsDropdown from "./InstructionsDropdown.jsx";

const UrlInput = ({ onSubmit, isSidebarOpen, toggleSidebar, isInstructionsOpen, toggleInstructions }) => {
  const [url, setUrl] = useState("");
  const [customSitemapTags, setCustomSitemapTags] = useState("");
  const [wantedWords, setWantedWords] = useState("");
  const [searchSubpages, setSearchSubpages] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = {
      url,
      customSitemapTags: searchSubpages ? customSitemapTags : "",
      wantedWords: searchSubpages ? wantedWords : "",
      searchSubpages,
    };

    onSubmit(formData);
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
        <div className="absolute top-16 right-[-40px] mr-4 mt-3" > {/* Adjust top offset here */}
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
              required
            />
          </div>

          <div className="mb-6 flex items-center">
            <input
              type="checkbox"
              checked={searchSubpages}
              onChange={() => setSearchSubpages(!searchSubpages)}
              className="mr-3"
            />
            <label className="text-gray-700">Search subpages for furniture</label>
          </div>

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
            className="bg-blue-500 text-white w-full py-2 rounded"
          >
            Search Furniture
          </button>
        </form>
      </div>
    </div>
  );
};

export default UrlInput;
