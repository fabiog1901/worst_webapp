<template>
  <section
    class="m-0 flex h-16 w-full flex-row items-center justify-evenly bg-gray-300 bg-opacity-90 shadow-lg dark:bg-gray-800"
  >
    <h5
      class="my-auto ml-2 mr-auto text-xl font-semibold tracking-wider text-gray-600 text-opacity-80 transition duration-300 ease-in-out dark:text-gray-400"
    ></h5>
    <div id="dark-theme" class="top-navigation-icon" v-on:click="toggleTheme">
      <svg
        v-if="userTheme === 'dark'"
        id="sun-icon"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        class="h-6 w-6"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z"
        />
      </svg>

      <svg
        v-else
        id="moon-icon"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        class="h-6 w-6"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z"
        />
      </svg>
    </div>
    <div
      id="search-box"
      class="ml-0 mr-0 flex h-9 w-1/5 items-center justify-start rounded-md bg-gray-400 px-2 text-gray-400 shadow-md transition duration-300 ease-in-out dark:bg-gray-600"
    >
      <input
        class="w-full rounded bg-transparent pl-1 font-sans font-semibold text-gray-400 placeholder-gray-500 outline-none"
        type="text"
        placeholder="Search..."
      />
      <svg
        id="magnifying-glass-icon"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        class="top-navigation-icon h-6 w-6"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
        />
      </svg>
    </div>
    <div class="top-navigation-icon">
      <svg
        id="bell-icon"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        class="ml-auto mr-4 h-6 w-6"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0"
        />
      </svg>
    </div>
    <div class="top-navigation-icon">
      <svg
        id="user-circle-icon"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        class="h-6 w-6"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M17.982 18.725A7.488 7.488 0 0012 15.75a7.488 7.488 0 00-5.982 2.975m11.963 0a9 9 0 10-11.963 0m11.963 0A8.966 8.966 0 0112 21a8.966 8.966 0 01-5.982-2.275M15 9.75a3 3 0 11-6 0 3 3 0 016 0z"
        />
      </svg>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

const userTheme = ref("light");

onMounted(() => {
  const initUserTheme = getTheme() || getMediaPreference();
  setTheme(initUserTheme);
});

const toggleTheme = () => {
  const activeTheme = localStorage.getItem("user-theme");
  if (activeTheme === "dark") {
    setTheme("light");
  } else {
    setTheme("dark");
  }
};

const getTheme = () => {
  return localStorage.getItem("user-theme");
};

const setTheme = (theme: string) => {
  localStorage.setItem("user-theme", theme);
  userTheme.value = theme;
  document.documentElement.className = theme;
};

const getMediaPreference = () => {
  const hasDarkPreference = window.matchMedia(
    "(prefers-color-scheme: dark)"
  ).matches;
  if (hasDarkPreference) {
    return "dark";
  } else {
    return "light";
  }
};
</script>

<style scoped>
.top-navigation-icon {
  @apply ml-4
    mr-3 cursor-pointer
    text-gray-600 transition duration-300 ease-in-out 
    hover:text-pink-400 dark:text-gray-400 
    dark:hover:text-pink-400;
}
</style>
