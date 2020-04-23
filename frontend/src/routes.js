import NotFound from "@/pages/NotFound";
import Home from "@/pages/Home";
import Collection from "@/pages/Collection";

export const routes = [
  NotFound,
  {
    home: {
      path: "/",
      component: Home
    },
    collection: {
      path: "/collections/:name",
      component: Collection
    },
  }
];
