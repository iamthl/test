import { Button, DialogTitle, Text } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { FaTrash } from "react-icons/fa"
import { useNavigate } from "@tanstack/react-router"

import { ItemsService } from "@/client"
import {
  DialogActionTrigger,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "@/components/ui/dialog"
import useCustomToast from "@/hooks/useCustomToast"

const DeleteItem = ({ id }: { id: string }) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const navigate = useNavigate()
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = useForm()

  const deleteItem = async (id: string) => {
    await ItemsService.deleteItem({ id: id })
  }

  const mutation = useMutation({
    mutationFn: deleteItem,
    onSuccess: () => {
      showSuccessToast("Tài sản đã được xoá thành công.")
      setIsOpen(false)
      navigate({ to: "/asset" })
    },
    onError: () => {
      showErrorToast("Đã xảy ra lỗi khi xoá tài sản.")
    },
    onSettled: () => {
      queryClient.invalidateQueries()
    },
  })

  const onSubmit = async () => {
    mutation.mutate(id)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      role="alertdialog"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <button
          className="flex items-center gap-2 w-full px-4 py-2 text-[#FF2A3C] hover:bg-[#18191B]"
          onClick={(e) => e.stopPropagation()}
          data-action-button="true"
        >
          <FaTrash /> Xoá
        </button>
      </DialogTrigger>

      <DialogContent onClick={(e) => e.stopPropagation()}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogCloseTrigger />
          <DialogHeader>
            <DialogTitle>Xoá tài sản</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>
              Tài sản này sẽ bị xoá vĩnh viễn. Bạn có chắc chắn không? Bạn sẽ không thể hoàn tác hành động này.
            </Text>
          </DialogBody>

          <DialogFooter gap={2}>
            <DialogActionTrigger asChild>
              <Button
                variant="subtle"
                colorPalette="gray"
                disabled={isSubmitting}
              >
                Hủy
              </Button>
            </DialogActionTrigger>
            <Button
              variant="solid"
              colorPalette="red"
              loading={isSubmitting}
              onClick={(e) => {
                e.stopPropagation();
                e.preventDefault();
                onSubmit();
              }}
            >
              Xoá
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </DialogRoot>
  )
}

export default DeleteItem
