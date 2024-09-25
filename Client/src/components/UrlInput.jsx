import React, { useState } from "react";

const UrlInput = ({ onSubmit }) => {
  const [url, setUrl] = useState("");
  const [customTags, setCustomTags] = useState("");
  const [customWords, setCustomWords] = useState("");
  const [searchSubpages, setSearchSubpages] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const formData = {
      url,
      customTags: searchSubpages ? customTags : "",
      customWords: searchSubpages ? customWords : "",
      searchSubpages,
    };

    try {
      const response = await axios.post(
        import.meta.env.VITE_ML_BACKEND_URL + "/scrape",
        formData,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      console.log("Response from backend:", response.data);
      onSubmit && onSubmit(response.data);
    } catch (error) {
      setError(error.message);
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4 max-w-full">
      <h1 className="text-4xl font-bold text-gray-900 mb-6 text-center max-w-full pb-6">
        Hello, my name is FurniMax !
      </h1>

      <h2 className="text-2xl font-semibold text-gray-700 mb-4 pb-20">Give me a URL and I will help you find the furniture of your dreams!</h2>

      <div className="flex flex-col lg:flex-row w-full max-w-[1280px] space-y-6 lg:space-y-0 lg:space-x-6">

        <div className="flex-1 lg:w-2/3 bg-white p-8 rounded-lg shadow-md">
          {/* Form */}
          <form onSubmit={handleSubmit}>
            {/* URL Input */}
            <div className="mb-6">
              <label className="block text-gray-700 text-lg mb-2" htmlFor="urlInput">
                Website URL:
              </label>
              <input
                type="url"
                id="urlInput"
                placeholder="https://myfurniture.com/furniture"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="appearance-none border border-gray-300 w-full text-gray-700 py-3 px-4 leading-tight focus:outline-none focus:border-blue-500 rounded-lg"
                required
              />
            </div>

            {/* Search Subpages Checkbox */}
            <div className="mb-6 flex items-center">
              <input
                type="checkbox"
                checked={searchSubpages}
                onChange={() => setSearchSubpages(!searchSubpages)}
                className="mr-3 h-5 w-5"
              />
              <label className="text-gray-700 text-lg">Search subpages for furniture</label>
            </div>

            {/* Custom Words in URLs - Shown conditionally */}
            {searchSubpages && (
              <div className="mb-6">
                <label className="block text-gray-700 text-lg mb-2" htmlFor="customWordsInput">
                  Custom Paths in URLs:
                </label>
                <input
                  type="text"
                  id="customWordsInput"
                  placeholder="Enter custom paths separated by commas (e.g., /products/, /furniture/)"
                  value={customWords}
                  onChange={(e) => setCustomWords(e.target.value)}
                  className="appearance-none border border-gray-300 w-full text-gray-700 py-3 px-4 leading-tight focus:outline-none focus:border-blue-500 rounded-lg"
                />
              </div>
            )}

            {/* Custom Web Tags Input - Shown conditionally */}
            {searchSubpages && (
              <div className="mb-6">
                <label className="block text-gray-700 text-lg mb-2" htmlFor="customTagsInput">
                  Custom XML Tags:
                </label>
                <input
                  type="text"
                  id="customTagsInput"
                  placeholder="Enter custom tags separated by commas ( 'loc' is used by default) - Fill only for scraping sitemaps!"
                  value={customTags}
                  onChange={(e) => setCustomTags(e.target.value)}
                  className="appearance-none border border-gray-300 w-full text-gray-700 py-3 px-4 leading-tight focus:outline-none focus:border-blue-500 rounded-lg"
                />
              </div>
            )}

            {/* Submit Button */}
            <div className="flex justify-center">
              <button
                type="submit"
                className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:shadow-outline transition-all duration-300"
              >
                Search Furniture
              </button>
            </div>
          </form>
        </div>

        {/* Description Card */}
        <div className="flex-1 lg:w-1/3 bg-gray-200 p-8 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">How to Use</h2>
          <p className="text-gray-700 mb-4">
            1. Enter a valid website URL in the input box on the left. The link can lead to any website or sitemap.
          </p>
          <p className="text-gray-700 mb-4">
            2. If you'd like to search the subpages of the website for furniture products, check the "Search subpages for furniture" box. It will go through all the href links on the website if you did not provide a sitemap URL.
          </p>
          <p className="text-gray-700 mb-4">
            3. Optionally, you can enter custom paths in URLs (e.g., /products/, /furniture/) to refine your search. Perhaps you know the website structure and want to search only for certain paths that contain what you desire. I strongly encourage using this since the scraping algorithm will catch a lot of irrelevant links otherwise.
          </p>
          <p className="text-gray-700">
            4. If you're scraping sitemaps, you can provide custom tags (specific XML tags like xhtml:link) for satisfying any sitemap format. If left empty, the default tag 'loc' will be used (commonly used in sitemaps).
          </p>
        </div>
      </div>
    </div>
  );
};

export default UrlInput;
