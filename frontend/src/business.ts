export type ServiceQuestion = { id: string; label: string; required: boolean };
export type BusinessService = {
  id: string;
  name: string;
  description: string;
  duration_minutes: number;
  price_cents: number | null;
  questions: ServiceQuestion[];
};
export type BusinessProfile = {
  name: string;
  domain: "dealership" | "salon";
  about: string;
  contact: string;
  time_zone: string;
  hours: { day: string; opens: string | null; closes: string | null }[];
  services: BusinessService[];
  faqs: { question: string; answer: string }[];
};
export type Workspace = {
  id: string;
  name: string;
  role: "owner" | "staff";
  revision: number;
  profile: BusinessProfile | null;
  published_revision: number | null;
  published: BusinessProfile | null;
};
export function exampleProfile(
  name: string,
  domain: "dealership" | "salon",
): BusinessProfile {
  const salon = domain === "salon";
  return {
    name,
    domain,
    about: salon
      ? "Tell us which service you are interested in. Our team will follow up."
      : "Explore our vehicles and ask our team about service.",
    contact: "Update with the public business contact",
    time_zone: "America/New_York",
    hours: [
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday",
      "Saturday",
      "Sunday",
    ].map((day, index) => ({
      day,
      opens: index < 5 ? "09:00" : null,
      closes: index < 5 ? "17:00" : null,
    })),
    services: [
      {
        id: salon ? "haircut" : "vehicle-service",
        name: salon ? "Haircut consultation" : "Vehicle service inquiry",
        description:
          "Submit a request for staff review. Times are arranged by staff.",
        duration_minutes: salon ? 45 : 30,
        price_cents: null,
        questions: salon
          ? [
              {
                id: "preferred-stylist",
                label: "Do you have a preferred stylist?",
                required: true,
              },
              {
                id: "service-interest",
                label: "What would you like done?",
                required: true,
              },
            ]
          : [
              {
                id: "vehicle",
                label: "What is the year, make and model of your vehicle?",
                required: true,
              },
              {
                id: "requested-work",
                label: "What service does your vehicle need?",
                required: true,
              },
            ],
      },
    ],
    faqs: [
      {
        question: "How do I request an appointment?",
        answer:
          "Send an inquiry below. Staff will contact you to arrange a time.",
      },
    ],
  };
}
