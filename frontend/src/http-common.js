import axios from "axios";
import axiosDefaults from "axios/lib/defaults";

axiosDefaults.xsrfCookieName = "csrftoken"
axiosDefaults.xsrfHeaderName = "X-CSRFToken"

export default axios.create({
  baseURL: "/api",
  headers: {
    "Content-type": "application/json",
  }
});