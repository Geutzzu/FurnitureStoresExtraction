import * as React from "react";
import * as ReactDOM from "react-dom/client";
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import App from "./App";
import "./index.css";
import UrlInput from "./components/UrlInput.jsx";
import ProductTable from "./components/ProductTable.jsx";
import ProductApp from "./components/ProductApp.jsx";


/// our app will contain only the ProductApp component (and its children) since that's all we need and use
const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        path: "/",
        element: (
            <>
                <ProductApp />
            </>
        )
      },
    ],
  },

]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);