<template>
  <Dialog
    v-model:visible="productDialog"
    v-bind:style="{ width: '450px' }"
    header="Product Details"
    v-bind:modal="true"
    class="p-fluid"
  >
    <img
      v-if="product.image"
      v-bind:src="`https://primefaces.org/cdn/primevue/images/product/${product.image}`"
      v-bind:alt="product.image"
      class="m-auto block pb-3"
    />
    <div class="field">
      <label for="name">Name</label>
      <InputText
        id="name"
        v-model.trim="product.name"
        required="true"
        autofocus
        v-bind:class="{ 'p-invalid': submitted && !product.name }"
      />
      <small v-if="submitted && !product.name" class="p-error"
        >Name is required.</small
      >
    </div>
    <div class="field">
      <label for="description">Description</label>
      <Textarea
        id="description"
        v-model="product.description"
        required="true"
        rows="3"
        cols="20"
      />
    </div>

    <div class="field">
      <label for="inventoryStatus" class="mb-3">Inventory Status</label>
      <Dropdown
        id="inventoryStatus"
        v-model="product.inventoryStatus"
        v-bind:options="statuses"
        option-label="label"
        placeholder="Select a Status"
      >
        <template v-slot:value="slotProps">
          <div v-if="slotProps.value && slotProps.value.value">
            <Tag
              v-bind:value="slotProps.value.value"
              v-bind:severity="getStatusLabel(slotProps.value.label)"
            />
          </div>
          <div v-else-if="slotProps.value && !slotProps.value.value">
            <Tag
              v-bind:value="slotProps.value"
              v-bind:severity="getStatusLabel(slotProps.value)"
            />
          </div>
          <span v-else>
            {{ slotProps.placeholder }}
          </span>
        </template>
      </Dropdown>
    </div>

    <div class="field">
      <label class="mb-3">Category</label>
      <div class="formgrid grid">
        <div class="field-radiobutton col-6">
          <RadioButton
            id="category1"
            v-model="product.category"
            name="category"
            value="Accessories"
          />
          <label for="category1">Accessories</label>
        </div>
        <div class="field-radiobutton col-6">
          <RadioButton
            id="category2"
            v-model="product.category"
            name="category"
            value="Clothing"
          />
          <label for="category2">Clothing</label>
        </div>
        <div class="field-radiobutton col-6">
          <RadioButton
            id="category3"
            v-model="product.category"
            name="category"
            value="Electronics"
          />
          <label for="category3">Electronics</label>
        </div>
        <div class="field-radiobutton col-6">
          <RadioButton
            id="category4"
            v-model="product.category"
            name="category"
            value="Fitness"
          />
          <label for="category4">Fitness</label>
        </div>
      </div>
    </div>

    <div class="formgrid grid">
      <div class="field col">
        <label for="price">Price</label>
        <InputNumber
          id="price"
          v-model="product.price"
          mode="currency"
          currency="USD"
          locale="en-US"
        />
      </div>
      <div class="field col">
        <label for="quantity">Quantity</label>
        <InputNumber id="quantity" v-model="product.quantity" integeronly />
      </div>
    </div>
    <template v-slot:footer>
      <Button label="Cancel" icon="pi pi-times" text v-on:click="hideDialog" />
      <Button label="Save" icon="pi pi-check" text v-on:click="saveProduct" />
    </template>
  </Dialog>

  <Dialog
    v-model:visible="deleteProductDialog"
    v-bind:style="{ width: '450px' }"
    header="Confirm"
    v-bind:modal="true"
  >
    <div class="confirmation-content">
      <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
      <span v-if="product"
        >Are you sure you want to delete <b>{{ product.name }}</b
        >?</span
      >
    </div>
    <template v-slot:footer>
      <Button
        label="No"
        icon="pi pi-times"
        text
        v-on:click="deleteProductDialog = false"
      />
      <Button label="Yes" icon="pi pi-check" text v-on:click="deleteProduct" />
    </template>
  </Dialog>

  <Dialog
    v-model:visible="deleteProductsDialog"
    v-bind:style="{ width: '450px' }"
    header="Confirm"
    v-bind:modal="true"
  >
    <div class="confirmation-content">
      <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
      <span v-if="product"
        >Are you sure you want to delete the selected products?</span
      >
    </div>
    <template v-slot:footer>
      <Button
        label="No"
        icon="pi pi-times"
        text
        v-on:click="deleteProductsDialog = false"
      />
      <Button
        label="Yes"
        icon="pi pi-check"
        text
        v-on:click="deleteSelectedProducts"
      />
    </template>
  </Dialog>
</template>



<script setup lang="ts">

import Tag from "primevue/tag";
import Button from "primevue/button";
// import FileUpload from "primevue/fileupload";
import Dialog from "primevue/dialog";
import InputNumber from "primevue/inputnumber";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import Dropdown from "primevue/dropdown";
import RadioButton from "primevue/radiobutton";
import { useToast } from "primevue/usetoast";


const productDialog = ref(false);
const deleteProductDialog = ref(false);
const deleteProductsDialog = ref(false);
const product = ref({});

const toast = useToast();
const submitted = ref(false);

const saveProduct = () => {
  submitted.value = true;

  if (product.value.name.trim()) {
    if (product.value.id) {
      product.value.inventoryStatus = product.value.inventoryStatus.value
        ? product.value.inventoryStatus.value
        : product.value.inventoryStatus;
      products.value[findIndexById(product.value.id)] = product.value;
      toast.add({
        severity: "success",
        summary: "Successful",
        detail: "Product Updated",
        life: 3000,
      });
    } else {
      product.value.id = createId();
      product.value.code = createId();
      product.value.image = "product-placeholder.svg";
      product.value.inventoryStatus = product.value.inventoryStatus
        ? product.value.inventoryStatus.value
        : "INSTOCK";
      products.value.push(product.value);
      toast.add({
        severity: "success",
        summary: "Successful",
        detail: "Product Created",
        life: 3000,
      });
    }

    productDialog.value = false;
    product.value = {};
  }
};
const editProduct = (prod) => {
  product.value = { ...prod };
  productDialog.value = true;
};
const confirmDeleteProduct = (prod) => {
  product.value = prod;
  deleteProductDialog.value = true;
};
const deleteProduct = () => {
  products.value = products.value.filter((val) => val.id !== product.value.id);
  deleteProductDialog.value = false;
  product.value = {};
  toast.add({
    severity: "success",
    summary: "Successful",
    detail: "Product Deleted",
    life: 3000,
  });
};

const deleteSelectedProducts = () => {
  products.value = products.value.filter(
    (val) => !selectedProducts.value.includes(val)
  );
  deleteProductsDialog.value = false;
  selectedProducts.value = null;
  toast.add({
    severity: "success",
    summary: "Successful",
    detail: "Products Deleted",
    life: 3000,
  });
};

const openNew = () => {
  product.value = {};
  submitted.value = false;
  productDialog.value = true;
};


const createId = () => {
  let id = "";
  var chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (var i = 0; i < 5; i++) {
    id += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return id;
};
const hideDialog = () => {
  productDialog.value = false;
  submitted.value = false;
};

const confirmDeleteSelected = () => {
  deleteProductsDialog.value = true;
};

const findIndexById = (id) => {
  let index = -1;
  for (let i = 0; i < products.value.length; i++) {
    if (products.value[i].id === id) {
      index = i;
      break;
    }
  }

  return index;
};
</script>