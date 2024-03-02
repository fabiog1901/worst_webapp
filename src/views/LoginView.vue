<template>
  <section
    class="align-center flex h-screen flex-col justify-center bg-slate-300 dark:bg-slate-700"
  >
    <div
      class="m-8 flex justify-center text-5xl font-semibold text-gray-700 dark:text-gray-200"
    >
      Worst
    </div>
    <div class="flex justify-center">
      <div
        class="h-16 w-fit cursor-pointer rounded-lg bg-slate-500 p-4 text-center text-2xl text-white hover:bg-slate-400"
        v-on:click="sso_login"
      >
        Login with SSO
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores/authStore";
import { generateRandomString, pkceChallengeFromVerifier } from "@/utils/utils";

const authStore = useAuthStore();

const sso_login = async () => {
  const oidc_config = await authStore.get_auth_config();

  localStorage.setItem("oidc_config", JSON.stringify(oidc_config));

  // Create and store a random "state" value
  var state = generateRandomString();
  localStorage.setItem("pkce_state", state);

  // Create and store a new PKCE code_verifier (the plaintext random secret)
  var code_verifier = generateRandomString();
  localStorage.setItem("pkce_code_verifier", code_verifier);

  // Hash and base64-urlencode the secret to use as the challenge
  var code_challenge = await pkceChallengeFromVerifier(code_verifier);

  // Build the authorization URL
  const url =
    oidc_config.authorization_endpoint +
    "?response_type=code" +
    "&client_id=" +
    encodeURIComponent(oidc_config.client_id) +
    "&state=" +
    encodeURIComponent(state) +
    "&scope=" +
    encodeURIComponent(oidc_config.requested_scopes) +
    "&redirect_uri=" +
    encodeURIComponent(oidc_config.redirect_uri) +
    "&code_challenge=" +
    encodeURIComponent(code_challenge) +
    "&code_challenge_method=S256";

  // Redirect to the authorization server
  window.location = url;
};
</script>
