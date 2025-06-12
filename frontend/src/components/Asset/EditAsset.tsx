import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaEdit, FaCheck, FaTimes } from "react-icons/fa"

import { type ApiError, type ItemPublic, ItemsService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

interface EditItemProps {
  item: ItemPublic;
  onCancel: () => void;
  onSave: () => void;
}

interface ItemUpdateForm {
  name: string;
  value: number;
  cumulativeReturn: number;
  investmentDuration: string;
}

const EditItem = ({ item, onCancel, onSave }: EditItemProps) => {
  const queryClient = useQueryClient();
  const { showSuccessToast } = useCustomToast();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ItemUpdateForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: item.title,
      value: item.description
        ? JSON.parse(item.description).value
        : undefined,
      cumulativeReturn: item.description
        ? JSON.parse(item.description).cumulativeReturn
        : undefined,
      investmentDuration: item.description ? JSON.parse(item.description).investmentDuration : "",
    },
  });

  console.log("item.description:", item.description);
  console.log("Parsed value:", item.description ? JSON.parse(item.description).value : undefined);
  console.log("Parsed cumulativeReturn:", item.description ? JSON.parse(item.description).cumulativeReturn : undefined);

  const mutation = useMutation({
    mutationFn: (data: ItemUpdateForm) => {
      return ItemsService.updateItem({
        id: item.id,
        requestBody: {
          title: data.name,
          description: JSON.stringify({
            value: data.value,
            cumulativeReturn: data.cumulativeReturn,
            investmentDuration: data.investmentDuration,
          }),
        },
      });
    },
    onSuccess: () => {
      showSuccessToast("Cập nhật tài sản thành công.");
      reset();
      onSave();
    },
    onError: (err: ApiError) => {
      handleError(err);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["items"] });
    },
  });

  const onSubmit: SubmitHandler<ItemUpdateForm> = (data) => {
    mutation.mutate(data);
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="flex flex-wrap gap-4 items-end bg-[#23232B] p-2 rounded-lg"
    >
      <div>
        <label className="block text-sm mb-1 text-white">Tên tài sản</label>
        <input
          type="text"
          {...register("name", { required: true })}
          className="px-2 py-1 rounded bg-[#18191B] text-white border border-gray-600"
          required
        />
      </div>
      <div>
        <label className="block text-sm mb-1 text-white">Giá trị</label>
        <input
          type="number"
          {...register("value", { required: true, valueAsNumber: true })}
          className="px-2 py-1 rounded bg-[#18191B] text-white border border-gray-600"
          required
        />
      </div>
      <div>
        <label className="block text-sm mb-1 text-white">Lợi nhuận tích luỹ</label>
        <input
          type="number"
          {...register("cumulativeReturn", { required: true, valueAsNumber: true })}
          className="px-2 py-1 rounded bg-[#18191B] text-white border border-gray-600"
          required
        />
      </div>
      <div>
        <label className="block text-sm mb-1 text-white">Thời gian đầu tư</label>
        <input
          type="date"
          {...register("investmentDuration", { required: true })}
          className="px-2 py-1 rounded bg-[#18191B] text-white border border-gray-600"
          required
        />
      </div>
      <button
        type="submit"
        className="bg-[#FF2A3C] text-white font-semibold px-4 py-2 rounded-lg shadow hover:bg-[#e02432] transition-colors mt-2 flex items-center gap-2"
        disabled={isSubmitting}
      >
        <FaCheck /> Lưu
      </button>
      <button
        type="button"
        className="ml-2 px-4 py-2 rounded-lg border border-gray-600 text-white bg-transparent hover:bg-gray-700 transition-colors mt-2 flex items-center gap-2"
        onClick={onCancel}
      >
        <FaTimes /> Hủy
      </button>
    </form>
  );
};

export default EditItem
