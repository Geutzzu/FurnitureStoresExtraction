import React from 'react';
import QuestionMark from "./svg/QuestionMark.jsx";

const InstructionsDropdown = ({ isInstructionsOpen, toggleInstructions }) => {
  return (
    <div className="relative mb-4">
        { /* instructions button with icon */}
        <button
            className="bg-darkGraphite text-white px-2 py-2 rounded flex items-center justify-center hover:opacity-90"
            onClick={toggleInstructions}
        >
            <QuestionMark/>
        </button>

        { /* instructions dropdown */}
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
                    through all the href links on the website recursively if you did not provide a
                    sitemap URL.
                </p>
                <p className="mb-4">
                    3. Optionally, you can enter custom paths in URLs (e.g.,
                    /products/, /furniture/) to refine your search. Perhaps you know
                    the website structure and want to search only for certain paths that
                    contain what you desire. I strongly encourage using this since the
                    scraping algorithm might catch some irrelevant links otherwise.
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
