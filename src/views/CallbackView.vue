<template>
  <section></section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/stores/authStore";
import router from "@/router";

const authStore = useAuthStore();
const route = useRoute();

onMounted(async () => {
  authStore.oidc_config = JSON.parse(localStorage.getItem("oidc_config"));

  console.log(authStore.oidc_config);

  // authStore.get_token(route.query.code as string);

  // OAUTH REDIRECT HANDLING
  // If the server returned an authorization code, attempt to exchange it for an access token
  if (route.query.code) {
    // Verify state matches what we set at the beginning
    if (localStorage.getItem("pkce_state") != route.query.state) {
      alert("Invalid state");
    } else {
      // Exchange the authorization code for an access token
      const params = {
        grant_type: "authorization_code",
        code: route.query.code,
        client_id: authStore.oidc_config.client_id,
        redirect_uri: authStore.oidc_config.redirect_uri,
        code_verifier: localStorage.getItem("pkce_code_verifier"),
      };

      var request = new XMLHttpRequest();
      request.open("POST", authStore.oidc_config.token_endpoint, true);
      request.setRequestHeader(
        "Content-Type",
        "application/x-www-form-urlencoded; charset=UTF-8",
      );
      request.onload = function () {
        var body = {};
        try {
          body = JSON.parse(request.response);
        } catch (e) {}

        if (request.status == 200) {
          authStore.id_token = body.id_token;
          authStore.access_token = body.access_token;
          router.push(authStore.returnUrl.value || "/");
        } else {
          console.error(request, body);
        }
      };
      request.onerror = function () {
        error(request, {});
      };
      var body = Object.keys(params)
        .map((key) => key + "=" + params[key])
        .join("&");
      request.send(body);
    }

    // Clean these up since we don't need them anymore
    localStorage.removeItem("pkce_state");
    localStorage.removeItem("pkce_code_verifier");
  }
});
</script>
