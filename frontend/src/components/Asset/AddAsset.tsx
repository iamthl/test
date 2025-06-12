import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useEffect, useState } from "react"
import { FaPlus } from "react-icons/fa"

import { type ItemCreate, ItemsService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

type AssetForm = {
  name: string;
  value?: number | null;
  cumulativeReturn?: number | null;
  investmentDuration: string;
};

interface AddItemProps {
  showForm: boolean;
  setShowForm: (show: boolean) => void;
}

const AddItem = ({ showForm, setShowForm }: AddItemProps) => {
  const queryClient = useQueryClient();
  const { showSuccessToast } = useCustomToast();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<AssetForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
      value: undefined,
      cumulativeReturn: undefined,
      investmentDuration: "",
    },
  });

  useEffect(() => {
    if (!showForm) {
      reset();
    }
  }, [showForm, reset]);

  const mutation = useMutation({
    mutationFn: (data: AssetForm) => {
      const valueToSave = isNaN(data.value as number) ? null : data.value;
      const cumulativeReturnToSave = isNaN(data.cumulativeReturn as number) ? null : data.cumulativeReturn;

      return ItemsService.createItem({
        requestBody: {
          title: data.name,
          description: JSON.stringify({
            value: valueToSave,
            cumulativeReturn: cumulativeReturnToSave,
            investmentDuration: data.investmentDuration,
          }),
        },
      });
    },
    onSuccess: () => {
      showSuccessToast("Item created successfully.");
      reset();
      setShowForm(false);
    },
    onError: (err: ApiError) => {
      handleError(err);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["items"] });
    },
  });

  const onSubmit: SubmitHandler<AssetForm> = (data) => {
    mutation.mutate(data);
  };

  return (
    <>
      <div className="flex justify-end mb-4 mt-5">
        {!showForm && (
          <button
            className="bg-[#FF2A3C] text-white font-semibold px-4 py-2 rounded-lg shadow hover:bg-[#e02432] transition-colors flex items-center gap-2"
            onClick={() => setShowForm(true)}
          >
            <FaPlus /> Thêm tài sản
          </button>
        )}
      </div>
      {showForm && (
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="mb-4 flex flex-wrap gap-4 items-end bg-[#23232B] p-4 rounded-lg"
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
              {...register("value", { valueAsNumber: true })}
              className="px-2 py-1 rounded bg-[#18191B] text-white border border-gray-600"
            />
          </div>
          <div>
            <label className="block text-sm mb-1 text-white">Lợi nhuận tích luỹ</label>
            <input
              type="number"
              {...register("cumulativeReturn", { valueAsNumber: true })}
              className="px-2 py-1 rounded bg-[#18191B] text-white border border-gray-600"
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
            className="bg-[#FF2A3C] text-white font-semibold px-4 py-2 rounded-lg shadow hover:bg-[#e02432] transition-colors mt-2"
            disabled={isSubmitting}
          >
            Lưu
          </button>
          <button
            type="button"
            className="ml-2 px-4 py-2 rounded-lg border border-gray-600 text-white bg-transparent hover:bg-gray-700 transition-colors mt-2"
            onClick={() => { reset(); setShowForm(false); }}
          >
            Hủy
          </button>
        </form>
      )}
    </>
  );
}

export default AddItem
