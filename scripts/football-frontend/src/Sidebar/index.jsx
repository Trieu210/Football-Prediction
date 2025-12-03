// Sidebar.jsx
import React, { useEffect, useState } from "react";
import {
  SingleLink,
  StyledAccordion,
  StyledAccordionDetails,
  StyledAccordionSummary,
  StyledDrawer,
} from "./styles";
import { Link } from "react-router-dom";   // ⭐ add this

const Sidebar = ({ open, onClose }) => {
  const [expanded, setExpanded] = useState(false);
  const [leagues, setLeagues] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/leagues")
      .then((res) => res.json())
      .then((data) => {
        console.log("Loaded leagues:", data);
        setLeagues(data);
      })
      .catch((err) => console.error("Error fetching leagues", err));
  }, []);

  return (
    <StyledDrawer
      variant="temporary"
      anchor="left"
      open={open}
      onClose={onClose}
      sx={{
        "& .MuiDrawer-paper": {
          width: 270,
          background: "#0d1117",
          color: "#fff",
          paddingTop: "20px",
        },
      }}
    >
      <div style={{ padding: "0 16px", marginBottom: "20px" }}>
        <h2 style={{ margin: 0, fontSize: "20px", fontWeight: 700 }}>
          Football App
        </h2>
      </div>

      <StyledAccordion
        expanded={expanded === 0}
        onChange={() => setExpanded(expanded === 0 ? false : 0)}
      >
        <StyledAccordionSummary>
          <span style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <i className="icon icon-trophy" />
            Leagues
          </span>
          <i className="icon icon-chevron-down" />
        </StyledAccordionSummary>

        <StyledAccordionDetails>
          {leagues.length === 0 ? (
            <p style={{ color: "#999", fontSize: "14px" }}>Loading...</p>
          ) : (
            leagues.map((lg) => (
              <Link
                key={lg.league}
                to={`/league/${encodeURIComponent(lg.league)}`}  // ⭐ route param
                style={{
                  display: "block",
                  padding: "6px 0",
                  color: "#bbb",
                  textDecoration: "none",
                  fontSize: "14px",
                }}
              >
                {lg.league}
              </Link>
            ))
          )}
        </StyledAccordionDetails>
      </StyledAccordion>

      <SingleLink style={{ marginTop: "auto", padding: "15px" }}>
        <a href="/settings" style={{ color: "#fff", textDecoration: "none" }}>
          <i className="icon icon-sliders" /> Settings
        </a>
      </SingleLink>
    </StyledDrawer>
  );
};

export default Sidebar;
