import React from 'react';

const InstructionsDropdown = ({ isInstructionsOpen, toggleInstructions }) => {
  return (
    <div className="relative mb-4">
        <button
            className="bg-darkGraphite text-white px-2 py-2 rounded flex items-center justify-center hover:opacity-90"
            onClick={toggleInstructions}
        >
            {/* SVG for the Question Mark Icon */}
            <svg
                className="h-6 w-6"
                xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" fill="white"
                 version="1.1" id="Capa_1" viewBox="0 0 31.357 31.357"
                 xml:space="preserve">
            <g>
                <path
                    d="M15.255,0c5.424,0,10.764,2.498,10.764,8.473c0,5.51-6.314,7.629-7.67,9.62c-1.018,1.481-0.678,3.562-3.475,3.562   c-1.822,0-2.712-1.482-2.712-2.838c0-5.046,7.414-6.188,7.414-10.343c0-2.287-1.522-3.643-4.066-3.643   c-5.424,0-3.306,5.592-7.414,5.592c-1.483,0-2.756-0.89-2.756-2.584C5.339,3.683,10.084,0,15.255,0z M15.044,24.406   c1.904,0,3.475,1.566,3.475,3.476c0,1.91-1.568,3.476-3.475,3.476c-1.907,0-3.476-1.564-3.476-3.476   C11.568,25.973,13.137,24.406,15.044,24.406z"/>
            </g>
            </svg>
        </button>

        {isInstructionsOpen && (
            <div className="absolute top-12 left-0 w-[700px] bg-white border border-gray-300 p-4 shadow-lg rounded">
                <h2 className="text-2xl font-semibold mb-4">How to Use</h2>
                <p className="mb-4">
                    1. Enter a valid website URL in the input box on the left. The link
                    can lead to any website or sitemap. Alternatively, you can upload a
                    CSV file containing URLs. The CSV file should have a single column and each row should contain a
                    URL.
                    The rest of the settings regarding subpage scraping remain the same for each URL inside the CSV.
                </p>
                <p className="mb-4">
                    2. If you'd like to search the subpages of the website for furniture
                    products, check the "Search subpages for furniture" box. It will go
                    through all the href links on the website if you did not provide a
                    sitemap URL.
                </p>
                <p className="mb-4">
                    3. Optionally, you can enter custom paths in URLs (e.g.,
                    /products/, /furniture/) to refine your search. Perhaps you know
                    the website structure and want to search only for certain paths that
                    contain what you desire. I strongly encourage using this since the
                    scraping algorithm will catch a lot of irrelevant links otherwise.
                </p>
                <p className="mb-4">
                    4. If you're scraping sitemaps, you can provide custom tags
                    (specific XML tags like xhtml:link) for satisfying any sitemap
                    format. If left empty, the default tag 'loc' will be used (commonly
                    used in sitemaps).
                </p>
                <p className="mb-4">
                    5. I strongly recommend not refreshing the page until you see in the status bar that everything
                    was completed successfully. If you do you may have to wait for the process to finish without any
                    UI indication since the server part of the code is still running in the background (and its not easy
                    to cancel it without killing the server).
                </p>

            </div>
        )}
    </div>
  );
};

export default InstructionsDropdown;
