import { Box, Button, Container, Heading, VStack } from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FiLock } from "react-icons/fi"

import { type ApiError, type UpdatePassword, UsersService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { confirmPasswordRules, handleError, passwordRules } from "@/utils"
import { PasswordInput } from "../ui/password-input"

interface UpdatePasswordForm extends UpdatePassword {
  confirm_password: string
}

const ChangePassword = () => {
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    getValues,
    formState: { errors, isValid, isSubmitting },
  } = useForm<UpdatePasswordForm>({
    mode: "onBlur",
    criteriaMode: "all",
  })

  const mutation = useMutation({
    mutationFn: (data: UpdatePassword) =>
      UsersService.updatePasswordMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Password updated successfully.")
      reset()
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  const onSubmit: SubmitHandler<UpdatePasswordForm> = async (data) => {
    mutation.mutate(data)
  }

  return (
    <>
      <Container maxW="full">
        <Heading size="sm" py={4}>
          Change Password
        </Heading>
        <Box as="form" onSubmit={handleSubmit(onSubmit)}>
          <VStack gap={4} w={{ base: "100%", md: "sm" }}>
            <PasswordInput
              type="current_password"
              startElement={<FiLock />}
              {...register("current_password", passwordRules())}
              placeholder="Current Password"
              errors={errors}
              bg="#18191B"
              color="white"
              border="1px"
              borderColor="#393945"
              _focus={{ borderColor: "#4299E1" }}
              _hover={{ borderColor: "#4299E1" }}
            />
            <PasswordInput
              type="new_password"
              startElement={<FiLock />}
              {...register("new_password", passwordRules())}
              placeholder="New Password"
              errors={errors}
              bg="#18191B"
              color="white"
              border="1px"
              borderColor="#393945"
              _focus={{ borderColor: "#4299E1" }}
              _hover={{ borderColor: "#4299E1" }}
            />
            <PasswordInput
              type="confirm_password"
              startElement={<FiLock />}
              {...register("confirm_password", confirmPasswordRules(getValues))}
              placeholder="Confirm Password"
              errors={errors}
              bg="#18191B"
              color="white"
              border="1px"
              borderColor="#393945"
              _focus={{ borderColor: "#4299E1" }}
              _hover={{ borderColor: "#4299E1" }}
            />
          </VStack>
          <Button
            variant="solid"
            mt={4}
            type="submit"
            loading={isSubmitting}
            disabled={!isValid}
            py={2}
            px={4}
            rounded="md"
            bg="#FF2A3C"
            color="white"
            _hover={{ bg: "#e02432" }}
            _active={{ bg: "#c41c2c" }}
          >
            Save
          </Button>
        </Box>
      </Container>
    </>
  )
}
export default ChangePassword
