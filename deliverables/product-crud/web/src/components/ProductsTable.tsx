import type { Product } from "../types/product";
import { PRODUCT_STATUS_LABEL } from "../types/product";

interface ProductsTableProps {
  products: Product[];
  isFetching: boolean;
  onEdit: (product: Product) => void;
  onDelete: (product: Product) => void;
  deletingId?: string | null;
}

const currency = new Intl.NumberFormat("th-TH", {
  style: "currency",
  currency: "THB",
  minimumFractionDigits: 2,
});

export function ProductsTable({
  products,
  isFetching,
  onEdit,
  onDelete,
  deletingId,
}: ProductsTableProps) {
  if (!products.length && !isFetching) {
    return (
      <div className="empty">
        <p>ยังไม่มีสินค้า</p>
        <p className="empty__hint">เริ่มเพิ่มสินค้าชิ้นแรกของคุณได้เลย</p>
      </div>
    );
  }

  return (
    <div className={`table-wrap${isFetching ? " table-wrap--fetching" : ""}`}>
      <table className="table">
        <thead>
          <tr>
            <th>ชื่อสินค้า</th>
            <th>SKU</th>
            <th className="num">ราคา</th>
            <th className="num">สต็อก</th>
            <th>สถานะ</th>
            <th aria-label="การจัดการ" />
          </tr>
        </thead>
        <tbody>
          {products.map((product) => (
            <tr key={product.id}>
              <td>
                <div className="cell-title">{product.name}</div>
                {product.description && <div className="cell-sub">{product.description}</div>}
              </td>
              <td>
                <code>{product.sku}</code>
              </td>
              <td className="num">{currency.format(product.price)}</td>
              <td className="num">{product.stock}</td>
              <td>
                <span className={`badge badge--${product.status.toLowerCase()}`}>
                  {PRODUCT_STATUS_LABEL[product.status]}
                </span>
              </td>
              <td className="actions">
                <button type="button" className="btn btn--sm" onClick={() => onEdit(product)}>
                  แก้ไข
                </button>
                <button
                  type="button"
                  className="btn btn--sm btn--danger"
                  onClick={() => onDelete(product)}
                  disabled={deletingId === product.id}
                >
                  {deletingId === product.id ? "กำลังลบ…" : "ลบ"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
