export type VehicleStatus = 'processing' | 'pending-approval' | 'approved' | 'active' | 'maintenance';

export type ExpenseCategory = 'fuel' | 'parts' | 'documents' | 'custom';

export interface Vehicle {
  id: string;
  vin: string;
  licensePlate: string;
  brand: string;
  model: string;
  year: number;
  status: VehicleStatus;
  ownerId: string | null;
  ownerName: string | null;
  createdAt: Date;
  isActive: boolean; // true = активні (лізинг), false = очікуючі
  isSaved?: boolean; // збережене авто
}

export interface MaintenancePlan {
  id: string;
  vehicleId: string;
  task: string;
  description: string;
  recommendedDate: Date;
  completed: boolean;
  createdAt: Date;
}

export interface Owner {
  id: string;
  name: string;
  email: string;
  phone: string;
  telegramUsername?: string;
  activeVehicles: number;
  createdAt: Date;
}

export interface Expense {
  id: string;
  vehicleId: string;
  expenseType: 'service' | 'other';
  serviceId?: string;
  serviceName?: string;
  category: string;
  subcategory?: string;
  customSubcategory?: string;
  description: string;
  priceType: 'total' | 'quantity'; // загальна сума або ціна×кількість
  totalAmount?: number;
  unitPrice?: number;
  quantity?: number;
  currency: 'PLN';
  date: Date;
  invoiceId?: string;
}

export interface Invoice {
  id: string;
  number: string;
  expenseId: string;
  fileUrl?: string;
  fileName?: string;
  uploadedAt: Date;
}

export interface ChatMessage {
  id: string;
  ownerId: string;
  ownerName: string;
  vehicleId: string;
  vehiclePlate: string;
  text: string;
  sender: 'manager' | 'owner';
  timestamp: Date;
  read: boolean;
}

export interface Comment {
  id: string;
  vehicleId: string;
  authorId: string;
  authorName: string;
  text: string;
  createdAt: Date;
}

export interface Notification {
  id: string;
  type: 'message_sent' | 'maintenance_reminder' | 'status_change' | 'expense_added';
  title: string;
  message: string;
  vehicleId?: string;
  ownerId?: string;
  timestamp: Date;
  read: boolean;
}

export interface AIRecommendation {
  id: string;
  vehicleId: string;
  type: 'maintenance' | 'cost_alert' | 'efficiency';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  createdAt: Date;
}

export interface Service {
  id: string;
  name: string;
  address: string;
  phone: string;
  email?: string;
  activeVehicles: number;
  createdAt: Date;
}