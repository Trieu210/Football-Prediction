import React from "react";
import styles from "./styles.module.scss";

const Search = () => {
  return (
    <form className={styles.search}>
      <input
        className="text-12"
        type="search"
        id="globalSearch"
        placeholder="Search for leagues or teams…"
      />
      <label htmlFor="globalSearch">
        <i className="icon-search" />
      </label>
    </form>
  );
};

export default Search;
