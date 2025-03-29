<script lang="ts">
  import * as Dialog from './ui/dialog/index';
  import { Label } from './ui/label';
  import { Input } from './ui/input';
  import { Button } from './ui/button';
</script>

<main>
  <Dialog.Root>
    <Dialog.Trigger><Button variant="secondary" class="text-green-500">Edit</Button></Dialog.Trigger
    >
    <Dialog.Content class="max-w-6xl">
      <Dialog.Header>
        <Dialog.Title>Edit Receipt</Dialog.Title>
        <Dialog.Description>
          <form action="" class="flex gap-4">
            <div class="flex flex-col gap-2">
              <Label>Merchant Name</Label>
              <Input type="text" name="merchantName" placeholder="Merchant Name" />
            </div>
            <div class="flex flex-col gap-2">
              <Label>Category</Label>
              <Input type="text" name="category" placeholder="Category" />
            </div>
          </form>
        </Dialog.Description>
      </Dialog.Header>
    </Dialog.Content>
  </Dialog.Root>
</main>
