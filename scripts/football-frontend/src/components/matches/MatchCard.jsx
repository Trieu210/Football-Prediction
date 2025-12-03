// src/components/matches/MatchCard.jsx
import React from "react";
import "./index.css"

const MatchCard = ({ match, index }) => {
  const {
    home_team,
    away_team,
    home_goals,
    away_goals,
    date,
    league,
    season,
    prob_home_win,
    prob_draw,
    prob_away_win,
  } = match;

  // Format date nicely
  let formattedDate = "";
  if (date) {
    const d = new Date(date);
    formattedDate = isNaN(d.getTime())
      ? date
      : d.toLocaleString("en-GB", {
          day: "2-digit",
          month: "short",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        });
  }

  const ph = typeof prob_home_win === "number" ? prob_home_win : 0;
  const pd = typeof prob_draw === "number" ? prob_draw : 0;
  const pa = typeof prob_away_win === "number" ? prob_away_win : 0;
  const total = ph + pd + pa || 1;

  const fh = ph / total;
  const fd = pd / total;
  const fa = pa / total;

  const pct = (p) => `${(p * 100).toFixed(1)}%`;

  return (
    <div className="match-card">
      {/* Header line */}
      <div className="match-card-header">
        <div>
          <span className="match-league">{league}</span>
          <span className="match-season"> • {season}</span>
        </div>
        <div className="match-date">{formattedDate}</div>
      </div>

      {/* Teams + scores with Home / Away labels */}
      <div className="match-teams">
        <div className="team-row">
          <span className="team-label home-label">Home</span>
          <span className="team-name">{home_team}</span>
          <span className="team-score">
            {home_goals !== undefined && home_goals !== null
              ? home_goals
              : "-"}
          </span>
        </div>
        <div className="team-row">
          <span className="team-label away-label">Away</span>
          <span className="team-name">{away_team}</span>
          <span className="team-score">
            {away_goals !== undefined && away_goals !== null
              ? away_goals
              : "-"}
          </span>
        </div>
      </div>

      {/* One-line probability bar */}
      <div className="prob-bar">
        <div
          className="prob-segment home-segment"
          style={{ flex: fh }}
          title={`Home win: ${pct(ph)}`}
        >
          {pct(ph)}
        </div>
        <div
          className="prob-segment draw-segment"
          style={{ flex: fd }}
          title={`Draw: ${pct(pd)}`}
        >
          {pct(pd)}
        </div>
        <div
          className="prob-segment away-segment"
          style={{ flex: fa }}
          title={`Away win: ${pct(pa)}`}
        >
          {pct(pa)}
        </div>
      </div>
    </div>
  );
};

export default MatchCard;
