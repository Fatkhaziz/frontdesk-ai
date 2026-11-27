const paths: Record<string, string> = {
  brand: "M5 4h14v11H9l-4 4V4Z M9 8h6 M9 11h4",
  Listings: "M4 5h16v14H4V5Z M4 10h16 M10 10v9",
  "Owner knowledge": "m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z",
  Inquiries: "M4 5h16v12H9l-5 4V5Z M8 9h8 M8 13h5",
  "Business settings": "M4 7h16 M4 17h16 M8 4v6 M16 14v6",
  "System status": "M3 12h4l3-7 4 14 3-7h4",
  arrow: "M5 12h14 M13 6l6 6-6 6",
  logout: "M9 4H4v16h5 M9 12h11 M16 8l4 4-4 4",
};

export default function Icon({ name }: { name: string }) {
  return <svg className="ui-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d={paths[name] || paths.brand} /></svg>;
}
