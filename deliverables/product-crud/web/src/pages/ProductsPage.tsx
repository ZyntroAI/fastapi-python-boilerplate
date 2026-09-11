import { useEffect, useState } from "react";
import { ProductFormModal } from "../components/ProductFormModal";
import { ProductsTable } from "../components/ProductsTable";
import { useProductMutations } from "../hooks/useProductMutations";
import { useProducts } from "../hooks/useProducts";
import {
  DEFAULT_LIST_PARAMS,
  PRODUCT_STATUSES,
  PRODUCT_STATUS_LABEL,
  type ListProductsParams,
  type Product,
  type ProductStatus,
} from "../types/product";

const PAGE_SIZE_OPTIONS = [10, 20, 50];

export function ProductsPage() {
  const [params, setParams] = useState<ListProductsParams>(DEFAULT_LIST_PARAMS);
  const [searchInput, setSearchInput] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Product | null>(null);

  // Debounce the search box so typing does not fire a request per keystroke,
  // and reset to page 1 whenever the term changes.
  useEffect(() => {
    const handle = window.setTimeout(() => {
      setParams((prev) =>
        prev.search === searchInput ? prev : { ...prev, search: searchInput, page: 1 },
      );
    }, 300);
    return () => window.clearTimeout(handle);
  }, [searchInput]);

  const { data, isPending, isFetching, isError, error, refetch } = useProducts(params);
  const { remove } = useProductMutations();
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const items = data?.items ?? [];
  const meta = data?.meta;

  const handleDelete = async (product: Product) => {
    if (!window.confirm(`ลบ "${product.name}" ใช่หรือไม่?`)) return;
    setDeletingId(product.id);
    try {
      await remove.mutateAsync(product.id);
    } finally {
      setDeletingId(null);
    }
  };

  const openCreate = () => {
    setEditing(null);
    setModalOpen(true);
  };

  const openEdit = (product: Product) => {
    setEditing(product);
    setModalOpen(true);
  };

  return (
    <div className="page">
      <header className="page__header">
        <div>
          <h1>สินค้า</h1>
          <p className="page__sub">
            {meta ? `${meta.total} รายการ` : "กำลังโหลด…"}
          </p>
        </div>
        <button type="button" className="btn btn--primary" onClick={openCreate}>
          + เพิ่มสินค้า
        </button>
      </header>

      <div className="toolbar">
        <input
          className="toolbar__search"
          placeholder="ค้นหาจากชื่อ, SKU หรือรายละเอียด…"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />

        <select
          className="toolbar__select"
          value={params.status ?? ""}
          onChange={(e) =>
            setParams((prev) => ({
              ...prev,
              status: (e.target.value || undefined) as ProductStatus | undefined,
              page: 1,
            }))
          }
        >
          <option value="">ทุกสถานะ</option>
          {PRODUCT_STATUSES.map((status) => (
            <option key={status} value={status}>
              {PRODUCT_STATUS_LABEL[status]}
            </option>
          ))}
        </select>
      </div>

      {isError && (
        <div className="alert">
          <span>โหลดข้อมูลไม่สำเร็จ: {(error as Error).message}</span>
          <button type="button" className="btn btn--sm" onClick={() => void refetch()}>
            ลองใหม่
          </button>
        </div>
      )}

      {isPending ? (
        <div className="empty">
          <p>กำลังโหลดข้อมูล…</p>
        </div>
      ) : (
        <ProductsTable
          products={items}
          isFetching={isFetching}
          onEdit={openEdit}
          onDelete={handleDelete}
          deletingId={deletingId}
        />
      )}

      {meta && meta.totalPages > 0 && (
        <nav className="pagination" aria-label="การแบ่งหน้า">
          <button
            type="button"
            className="btn btn--sm"
            disabled={!meta.hasPrev}
            onClick={() => setParams((prev) => ({ ...prev, page: Math.max(1, prev.page - 1) }))}
          >
            ก่อนหน้า
          </button>

          <span className="pagination__status">
            หน้า {meta.page} จาก {meta.totalPages}
          </span>

          <button
            type="button"
            className="btn btn--sm"
            disabled={!meta.hasNext}
            onClick={() => setParams((prev) => ({ ...prev, page: prev.page + 1 }))}
          >
            ถัดไป
          </button>

          <label className="pagination__size">
            <span>ต่อหน้า</span>
            <select
              value={params.pageSize}
              onChange={(e) =>
                setParams((prev) => ({ ...prev, pageSize: Number(e.target.value), page: 1 }))
              }
            >
              {PAGE_SIZE_OPTIONS.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </label>
        </nav>
      )}

      <ProductFormModal open={modalOpen} product={editing} onClose={() => setModalOpen(false)} />
    </div>
  );
}
