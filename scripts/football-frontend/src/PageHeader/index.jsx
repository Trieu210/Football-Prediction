import React from "react";
import PropTypes from "prop-types";
import styles from "./styles.module.scss";

import Search from "./Search";
import User from "./User";

const PageHeader = ({ title }) => {
  return (
    <div
      className={`${styles.desktop} d-flex justify-content-between align-items-center g-20`}
    >
      <div className="d-flex align-items-center flex-1 g-30">
        <div className="flex-1">
          <h2 className={`${styles.title} h2 m-0`}>{title}</h2>
        </div>
      </div>

      <div className="d-flex align-items-center g-30">
        <Search />
        <User />
      </div>
    </div>
  );
};

PageHeader.propTypes = {
  title: PropTypes.string.isRequired,
};

export default PageHeader;
