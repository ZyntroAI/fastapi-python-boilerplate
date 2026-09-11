import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { useProductMutations } from "../hooks/useProductMutations";
import {
  PRODUCT_STATUSES,
  PRODUCT_STATUS_LABEL,
  productFormSchema,
  type Product,
  type ProductFormValues,
} from "../types/product";

interface ProductFormModalProps {
  open: boolean;
  product?: Product | null;
  onClose: () => void;
}

const EMPTY: ProductFormValues = {
  name: "",
  sku: "",
  description: "",
  price: 0,
  stock: 0,
  status: "DRAFT",
};

export function ProductFormModal({ open, product, onClose }: ProductFormModalProps) {
  const isEdit = Boolean(product);
  const { create, update } = useProductMutations({ onSuccess: () => onClose() });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ProductFormValues>({
    resolver: zodResolver(productFormSchema),
    defaultValues: EMPTY,
  });

  // Re-seed the form whenever the modal opens for a different record.
  useEffect(() => {
    if (!open) return;
    reset(
      product
        ? {
            name: product.name,
            sku: product.sku,
            description: product.description ?? "",
            price: product.price,
            stock: product.stock,
            status: product.status,
          }
        : EMPTY,
    );
  }, [open, product, reset]);

  if (!open) return null;

  const onSubmit = handleSubmit(async (values) => {
    if (product) {
      await update.mutateAsync({ id: product.id, values });
    } else {
      await create.mutateAsync(values);
    }
  });

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="product-form-title"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="modal__header">
          <h2 id="product-form-title">{isEdit ? "แก้ไขสินค้า" : "เพิ่มสินค้า"}</h2>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="ปิด">
            ×
          </button>
        </header>

        <form className="form" onSubmit={onSubmit} noValidate>
          <label className="field">
            <span>ชื่อสินค้า</span>
            <input {...register("name")} autoFocus placeholder="เช่น ประแจทอร์ก" />
            {errors.name && <em className="field__error">{errors.name.message}</em>}
          </label>

          <label className="field">
            <span>SKU</span>
            <input {...register("sku")} placeholder="เช่น TW-100" />
            {errors.sku && <em className="field__error">{errors.sku.message}</em>}
          </label>

          <div className="field-row">
            <label className="field">
              <span>ราคา</span>
              <input {...register("price")} type="number" step="0.01" min="0" />
              {errors.price && <em className="field__error">{errors.price.message}</em>}
            </label>

            <label className="field">
              <span>จำนวนในสต็อก</span>
              <input {...register("stock")} type="number" step="1" min="0" />
              {errors.stock && <em className="field__error">{errors.stock.message}</em>}
            </label>

            <label className="field">
              <span>สถานะ</span>
              <select {...register("status")}>
                {PRODUCT_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {PRODUCT_STATUS_LABEL[status]}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label className="field">
            <span>รายละเอียด</span>
            <textarea {...register("description")} rows={3} placeholder="รายละเอียดเพิ่มเติม (ไม่บังคับ)" />
            {errors.description && <em className="field__error">{errors.description.message}</em>}
          </label>

          <footer className="modal__footer">
            <button type="button" className="btn" onClick={onClose}>
              ยกเลิก
            </button>
            <button type="submit" className="btn btn--primary" disabled={isSubmitting}>
              {isSubmitting ? "กำลังบันทึก…" : isEdit ? "บันทึกการแก้ไข" : "เพิ่มสินค้า"}
            </button>
          </footer>
        </form>
      </div>
    </div>
  );
}
