import { styled } from "@mui/material/styles";
import Drawer from "@mui/material/Drawer";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";

export const StyledDrawer = styled(Drawer)({
  "& .MuiPaper-root": {
    backgroundColor: "#0d1117",
    color: "#fff",
    padding: "10px 0",
  },
});

export const StyledAccordion = styled(Accordion)({
  background: "transparent",
  color: "#fff",
  boxShadow: "none",
  "&:before": {
    display: "none",
  },
});

export const StyledAccordionSummary = styled(AccordionSummary)({
  padding: "0 20px",
  minHeight: 48,
  "& .MuiAccordionSummary-content": {
    justifyContent: "space-between",
    alignItems: "center",
  },
});

export const StyledAccordionDetails = styled(AccordionDetails)({
  background: "#161b22",
  padding: "10px 20px",
  display: "flex",
  flexDirection: "column",
  gap: "6px",
});

export const Link = styled("div")({
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  fontSize: "16px",
  gap: "10px",
});

export const SingleLink = styled("div")({
  padding: "10px 20px",
});
