import { useParams } from "react-router-dom";
import LeagueMatches from "../components/matches/LeagueMatches";

function LeaguePage() {
  const { leagueName } = useParams();

  // decode from URL, fallback just in case
  const decodedLeague = leagueName
    ? decodeURIComponent(leagueName)
    : "Premier League";

  return (
    <div style={{ padding: "20px" }}>
      <LeagueMatches league={decodedLeague} />
    </div>
  );
}

export default LeaguePage;
