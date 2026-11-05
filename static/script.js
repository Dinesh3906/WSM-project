"use strict";

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("search-form");
  const input = document.getElementById("query-input");
  const searchButton = document.getElementById("search-button");
  const clearButton = document.getElementById("clear-button");
  const count = document.getElementById("result-count");
  const emptyState = document.getElementById("empty-state");
  const resultContent = document.getElementById("result-content");

  function addTextElement(parent, tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    element.textContent = text;
    parent.appendChild(element);
    return element;
  }

  function showError(message) {
    emptyState.hidden = true;
    resultContent.hidden = false;
    resultContent.replaceChildren();
    addTextElement(resultContent, "p", "error-message", message);
    count.textContent = "Search could not be completed";
  }

  function renderResults(data) {
    emptyState.hidden = true;
    resultContent.hidden = false;
    resultContent.replaceChildren();

    if (data.status === "error" || data.status === "warning") {
      showError(data.message || "Please check your search query.");
      return;
    }

    const documents = Array.isArray(data.documents) ? data.documents : [];
    const total = Number(data.total_matching) || 0;
    count.textContent = total + (total === 1 ? " document found" : " documents found");
    addTextElement(resultContent, "p", "query-line", "Query: " + data.query);
    addTextElement(resultContent, "h3", "", "Matching documents");

    if (documents.length === 0) {
      addTextElement(resultContent, "p", "no-matches", "No documents matched this query.");
    } else {
      const matchList = document.createElement("ul");
      matchList.className = "match-list";
      documents.forEach(function (documentInfo) {
        const item = document.createElement("li");
        item.className = "match-card";
        addTextElement(item, "span", "doc-badge", documentInfo.doc_id || "DOC");
        const details = document.createElement("div");
        details.className = "doc-details";
        addTextElement(details, "div", "filename", documentInfo.filename || "Unnamed document");
        if (documentInfo.snippet) {
          addTextElement(details, "p", "snippet", documentInfo.snippet);
        }
        item.appendChild(details);
        matchList.appendChild(item);
      });
      resultContent.appendChild(matchList);
    }

    const expansions = data.expanded_wildcards || {};
    const patterns = Object.keys(expansions);
    if (patterns.length > 0) {
      addTextElement(resultContent, "h3", "", "Wildcard-expanded terms");
      patterns.forEach(function (pattern) {
        const terms = document.createElement("div");
        terms.className = "term-list";
        (expansions[pattern] || []).forEach(function (term) {
          addTextElement(terms, "span", "term-chip", term);
        });
        if (terms.childElementCount > 0) {
          resultContent.appendChild(terms);
        }
      });
    }
  }

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    const query = input.value.trim();
    if (!query) {
      showError("Enter a search query to continue.");
      input.focus();
      return;
    }

    searchButton.disabled = true;
    searchButton.textContent = "Searching…";
    try {
      const response = await fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query })
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || "The search request failed.");
      }
      renderResults(data);
    } catch (error) {
      showError(error.message || "Could not connect to the search service.");
    } finally {
      searchButton.disabled = false;
      searchButton.innerHTML = 'Search <span aria-hidden="true">↗</span>';
    }
  });

  clearButton.addEventListener("click", function () {
    input.value = "";
    resultContent.replaceChildren();
    resultContent.hidden = true;
    emptyState.hidden = false;
    count.textContent = "Ready when you are";
    input.focus();
  });

  document.querySelectorAll(".example-query").forEach(function (button) {
    button.addEventListener("click", function () {
      input.value = button.textContent.trim();
      input.focus();
    });
  });
});
