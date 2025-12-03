import React from "react";
import PropTypes from "prop-types";

const TeamRow = ({ name, score, isLeader, variant = "card" }) => {
  const fontSize = variant === "card" ? "1rem" : "1.125rem";

  return (
    <div
      className={`d-flex justify-content-between align-items-center g-20 ${
        isLeader ? "text-700 h3" : ""
      }`}
      style={{
        lineHeight: 1,
        fontSize,
        color: variant === "card" ? (isLeader ? "var(--header)" : "var(--text)") : "var(--header-dark)",
      }}
    >
      <div className="d-flex align-items-center g-8 flex-1">
        <span>{name}</span>
      </div>
      <span>{score}</span>
    </div>
  );
};

const MatchScoreItem = ({ match, variant = "card" }) => {
  const { home_team, away_team, home_goals, away_goals } = match;

  const leader =
    home_goals > away_goals
      ? "home"
      : home_goals < away_goals
      ? "away"
      : null;

  return (
    <div className={`d-flex flex-column ${variant === "card" ? "g-6" : "g-8"}`}>
      <TeamRow
        name={home_team}
        score={home_goals}
        isLeader={leader === "home"}
        variant={variant}
      />
      <TeamRow
        name={away_team}
        score={away_goals}
        isLeader={leader === "away"}
        variant={variant}
      />
    </div>
  );
};

MatchScoreItem.propTypes = {
  match: PropTypes.shape({
    home_team: PropTypes.string.isRequired,
    away_team: PropTypes.string.isRequired,
    home_goals: PropTypes.number.isRequired,
    away_goals: PropTypes.number.isRequired,
  }).isRequired,
  variant: PropTypes.oneOf(["card", "thumb"]),
};

export default MatchScoreItem;
