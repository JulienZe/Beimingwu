import { createRouter, createWebHashHistory } from "vue-router";
import store from "../store";

const Router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: "/",
      name: "Home",
      component: () => import("../views/Home.vue"),
      meta: {
        showInNavBar: true,
        icon: "mdi-home",
      },
    },
    {
      path: "/search",
      name: "Search",
      component: () => import("../views/Search.vue"),
      meta: {
        showInNavBar: true,
        keepAlive: true,
        icon: "mdi-magnify",
      },
    },
    {
      path: "/submit",
      name: "Submit",
      component: () => import("../views/Submit.vue"),
      meta: {
        showInNavBar: true,
        requiredLogin: true,
        keepAlive: true,
        icon: "mdi-transfer",
      },
    },
    {
      path: "/docs",
      name: "Docs",
      component: () => import("../views/Docs.vue"),
      meta: {
        showInNavBar: true,
        name: "Docs",
        icon: "mdi-book-open-page-variant",
      },
    },
    {
      path: "/user",
      name: "User",
      meta: {
        showInNavBar: true,
        icon: "mdi-account",
      },
      children: [
        {
          path: "/login",
          name: "Login",
          component: () => import("../views/Login.vue"),
          meta: {
            showInNavBar: true,
            hideWhenLoggedIn: true,
            icon: "mdi-login",
          },
        },
        {
          path: "/register",
          name: "Register",
          component: () => import("../views/Register.vue"),
          meta: {
            showInNavBar: true,
            hideWhenLoggedIn: true,
            icon: "mdi-account-plus",
            variant: "outlined",
            class: ["py-2.5 rounded-lg border-2"],
          },
        },
        {
          path: "/changepassword",
          name: "ChangePassword",
          component: () => import("../views/ChangePassword.vue"),
          meta: {
            showInNavBar: true,
            requiredLogin: true,
            name: "Change Password",
            icon: "mdi-account-edit",
            class: ["py-2.5 rounded-lg"],
          },
        },
        {
          path: "/mylearnware",
          name: "MyLearnware",
          component: () => import("../views/MyLearnware.vue"),
          meta: {
            name: "My Learnware",
            showInNavBar: true,
            requiredLogin: true,
            keepAlive: true,
            icon: "mdi-file-eye",
          },
        },
        {
          path: "/clienttoken",
          name: "ClientToken",
          component: () => import("../views/ClientToken.vue"),
          meta: {
            showInNavBar: true,
            requiredLogin: true,
            name: "Client Token",
            icon: "mdi-key",
            keepAlive: true,
          },
        },
        {
          path: "/logout",
          name: "Logout",
          component: () => import("../views/Logout.vue"),
          meta: {
            showInNavBar: true,
            requiredLogin: true,
            icon: "mdi-logout",
            variant: "outlined",
            class: ["py-2.5 rounded border-2"],
          },
        },
      ],
    },
    {
      path: "/language",
      name: "Language",
      meta: {
        showInNavBar: true,
        icon: "mdi-earth",
      },
      children: [
        {
          path: "/language/zh",
          name: "Chinese",
          component: () => import("../views/ChangeLanguage.vue"),
          meta: {
            showInNavBar: true,
            icon: "🇨🇳",
            variant: "outlined",
          },
        },
        {
          path: "/language/en",
          name: "English",
          component: () => import("../views/ChangeLanguage.vue"),
          meta: {
            showInNavBar: true,
            icon: "🇺🇸",
            variant: "outlined",
          },
        },
      ],
    },
    {
      path: "/learnwaredetail",
      name: "LearnwareDetail",
      component: () => import("../views/LearnwareDetail.vue"),
      meta: {
        showInNavBar: false,
        icon: "mdi-bullseye-arrow",
      },
    },
    {
      path: "/verify_email",
      name: "VerifyEmail",
      component: () => import("../views/VerifyEmail.vue"),
      meta: {
        showInNavBar: false,
        icon: "mdi-email-check-outline",
      },
    },
  ],
  scrollBehavior() {
    return { top: 0 };
  },
});

Router.beforeEach((to, from, next) => {
  if (from.name === to.name) {
    return next(false);
  }
  if (to.matched.some((record) => record.meta.requiredLogin)) {
    if (store && !store.getters.getLoggedIn) {
      store.commit("setShowGlobalError", true);
      store.commit("setGlobalErrorMsg", "Please login first.");
      next({
        path: "/login",
        query: { redirect: to.fullPath },
      });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default Router;