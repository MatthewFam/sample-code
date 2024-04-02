// Navigate to filtered list of projects based on selection on homepage of personal website (matthewfam.com).
// Written  2021.

function filteredProjects() {

  let selectedFilter = localStorage.getItem("selectedFilter");

  if (selectedFilter !== null) {
    filterTag(selectedFilter);
    window.history.replaceState({}, document.title, "/" + "filtered");
  }
  else {
    let urlParams = new URLSearchParams(window.location.search);
    let val = urlParams.get("tag");
    filterTag(val);

    window.history.replaceState({}, document.title, "/" + "filtered");
    localStorage.getItem("selectedFilter") = val;
  }

  // localStorage.clear();
}

if(document.readyState !== "loading") {
  // begin if not loading
  filteredProjects();
} else {
  // begin on DOM load
  document.addEventListener("DOMContentLoaded", function () {
      filteredProjects();
  });
}